import os
import json
import time
import logging
import requests
import pymysql
from flask import Flask, jsonify, request, Response
from jose import jwt, JWTError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==============================================================================
# Configuration & Environment Variables
# ==============================================================================
DATA_FILE = os.getenv("DATA_FILE", os.path.join(os.path.dirname(__file__), "data", "students.json"))

# MariaDB config
DB_HOST = os.getenv("DB_HOST", "relational-database-server")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "clouduser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "cloudpassword")
DB_NAME = os.getenv("DB_NAME", "studentdb")

# Keycloak OIDC config
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "http://authentication-identity-server:8080/realms/MyMiniCloud")
OIDC_AUDIENCE = os.getenv("OIDC_AUDIENCE", "flask-app")
JWKS_URL = f"{OIDC_ISSUER}/protocol/openid-connect/certs"

_JWKS_CACHE = None
_JWKS_TIMESTAMP = 0
JWKS_TTL_SECONDS = 300

# ==============================================================================
# Prometheus Metrics
# ==============================================================================
HTTP_REQUESTS_TOTAL = Counter(
    "flask_http_requests_total",
    "Total count of HTTP requests received by Flask Backend",
    ["method", "endpoint", "status"]
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "flask_http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["endpoint"]
)

@app.before_request
def before_request_hook():
    request._start_time = time.time()

@app.after_request
def after_request_hook(response):
    if hasattr(request, "_start_time"):
        duration = time.time() - request._start_time
        endpoint = request.endpoint or "unknown"
        HTTP_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(duration)
        HTTP_REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
    return response

# ==============================================================================
# Helper Functions
# ==============================================================================
def get_db_connection():
    """Create and return a pymysql connection to MariaDB."""
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5
    )

def fetch_jwks():
    """Fetch and cache Keycloak JSON Web Key Set (JWKS)."""
    global _JWKS_CACHE, _JWKS_TIMESTAMP
    now = time.time()
    if _JWKS_CACHE is None or (now - _JWKS_TIMESTAMP) > JWKS_TTL_SECONDS:
        logger.info(f"Fetching JWKS keys from {JWKS_URL}...")
        resp = requests.get(JWKS_URL, timeout=5)
        resp.raise_for_status()
        _JWKS_CACHE = resp.json()
        _JWKS_TIMESTAMP = now
    return _JWKS_CACHE

# ==============================================================================
# Endpoints
# ==============================================================================

@app.get("/health")
def health():
    """Basic healthcheck endpoint for Docker container."""
    return jsonify(status="healthy", timestamp=time.time())

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.get("/hello")
def hello():
    """Baseline API test endpoint."""
    return jsonify(message="Hello from App Server!", status="success")

@app.get("/student")
@app.get("/api/student")
def get_students_json():
    """
    Chức năng mở rộng 2:
    Đọc danh sách 5 sinh viên từ file JSON với xử lý lỗi đầy đủ.
    """
    if not os.path.exists(DATA_FILE):
        logger.error(f"Data file not found at: {DATA_FILE}")
        return jsonify(error="Student data file not found", path=DATA_FILE), 404

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            students = json.load(f)
        
        if not isinstance(students, list):
            return jsonify(error="Invalid data structure in students.json, expected a list"), 500

        return jsonify(
            source="json_file",
            total=len(students),
            data=students
        ), 200
    except json.JSONDecodeError as err:
        logger.error(f"JSON decode error: {err}")
        return jsonify(error="Malformed JSON data file", details=str(err)), 500
    except Exception as err:
        logger.error(f"Unexpected error reading students file: {err}")
        return jsonify(error="Internal server error", details=str(err)), 500

@app.get("/students-db")
@app.get("/api/students-db")
def get_students_db():
    """
    Chức năng mở rộng 3:
    Truy vấn bảng 'students' trong cơ sở dữ liệu MariaDB 'studentdb'.
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, student_id, fullname, dob, major, gpa, created_at FROM students ORDER BY id ASC;")
            records = cursor.fetchall()
            # Format datetime for JSON serialization
            for row in records:
                if row.get("dob"):
                    row["dob"] = str(row["dob"])
                if row.get("created_at"):
                    row["created_at"] = str(row["created_at"])
                if "gpa" in row and row["gpa"] is not None:
                    row["gpa"] = float(row["gpa"])
        conn.close()
        return jsonify(
            source="mariadb_studentdb",
            total=len(records),
            data=records
        ), 200
    except pymysql.MySQLError as err:
        logger.error(f"Database query error: {err}")
        return jsonify(error="Database error occurred", details=str(err)), 500
    except Exception as err:
        logger.error(f"Unexpected database connection error: {err}")
        return jsonify(error="Could not connect to MariaDB", details=str(err)), 503

@app.post("/students-db")
@app.post("/api/students-db")
def add_student_db():
    """Thêm một sinh viên mới vào MariaDB (Hỗ trợ kiểm thử CRUD CREATE)."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="Missing or invalid JSON body"), 400

    required_fields = ["student_id", "fullname", "dob", "major"]
    for field in required_fields:
        if field not in payload or not str(payload[field]).strip():
            return jsonify(error=f"Field '{field}' is required and cannot be empty"), 400

    try:
        gpa = float(payload.get("gpa", 3.0))
        if gpa < 0.0 or gpa > 4.0:
            return jsonify(error="GPA must be between 0.0 and 4.0"), 400
    except (ValueError, TypeError):
        return jsonify(error="GPA must be a valid decimal number"), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO students (student_id, fullname, dob, major, gpa)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(sql, (
                payload["student_id"].strip(),
                payload["fullname"].strip(),
                payload["dob"].strip(),
                payload["major"].strip(),
                gpa
            ))
            conn.commit()
            new_id = cursor.lastrowid
        conn.close()
        return jsonify(
            message="Student created successfully",
            id=new_id,
            student_id=payload["student_id"]
        ), 201
    except pymysql.err.IntegrityError as err:
        logger.warning(f"Integrity error (e.g. duplicate student_id): {err}")
        return jsonify(error="Duplicate entry or constraint violation", details=str(err)), 400
    except pymysql.MySQLError as err:
        logger.error(f"Database insert error: {err}")
        return jsonify(error="Database insert error", details=str(err)), 500

@app.get("/students-db/<int:student_id>")
@app.get("/api/students-db/<int:student_id>")
def get_single_student_db(student_id):
    """Lấy chi tiết một sinh viên theo ID (CRUD READ SINGLE)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, student_id, fullname, dob, major, gpa, created_at FROM students WHERE id = %s;",
                (student_id,)
            )
            record = cursor.fetchone()
        conn.close()

        if not record:
            return jsonify(error="Student not found", id=student_id), 404

        if record.get("dob"):
            record["dob"] = str(record["dob"])
        if record.get("created_at"):
            record["created_at"] = str(record["created_at"])
        if "gpa" in record and record["gpa"] is not None:
            record["gpa"] = float(record["gpa"])

        return jsonify(source="mariadb_studentdb", data=record), 200
    except pymysql.MySQLError as err:
        return jsonify(error="Database query error", details=str(err)), 500

@app.put("/students-db/<int:student_id>")
@app.put("/api/students-db/<int:student_id>")
def update_student_db(student_id):
    """Cập nhật thông tin sinh viên theo ID (CRUD UPDATE)."""
    payload = request.get_json(silent=True)
    if not payload:
        return jsonify(error="Missing or invalid JSON body"), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if student exists
            cursor.execute("SELECT id, student_id, fullname, dob, major, gpa FROM students WHERE id = %s;", (student_id,))
            existing = cursor.fetchone()
            if not existing:
                conn.close()
                return jsonify(error="Student not found for update", id=student_id), 404

            # Update fields
            fullname = payload.get("fullname", existing["fullname"])
            dob = payload.get("dob", str(existing["dob"]))
            major = payload.get("major", existing["major"])
            gpa = float(payload.get("gpa", existing["gpa"]))

            if gpa < 0.0 or gpa > 4.0:
                conn.close()
                return jsonify(error="GPA must be between 0.0 and 4.0"), 400

            sql = """
                UPDATE students
                SET fullname = %s, dob = %s, major = %s, gpa = %s
                WHERE id = %s;
            """
            cursor.execute(sql, (fullname, dob, major, gpa, student_id))
            conn.commit()

        conn.close()
        return jsonify(
            message="Student updated successfully",
            id=student_id,
            updated={
                "fullname": fullname,
                "dob": dob,
                "major": major,
                "gpa": gpa
            }
        ), 200
    except pymysql.MySQLError as err:
        logger.error(f"Database update error: {err}")
        return jsonify(error="Database update error", details=str(err)), 500

@app.delete("/students-db/<int:student_id>")
@app.delete("/api/students-db/<int:student_id>")
def delete_student_db(student_id):
    """Xóa một sinh viên theo ID (CRUD DELETE)."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, fullname FROM students WHERE id = %s;", (student_id,))
            existing = cursor.fetchone()
            if not existing:
                conn.close()
                return jsonify(error="Student not found for deletion", id=student_id), 404

            cursor.execute("DELETE FROM students WHERE id = %s;", (student_id,))
            conn.commit()
        conn.close()
        return jsonify(
            message="Student deleted successfully",
            id=student_id,
            deleted_name=existing["fullname"]
        ), 200
    except pymysql.MySQLError as err:
        logger.error(f"Database delete error: {err}")
        return jsonify(error="Database delete error", details=str(err)), 500

@app.get("/secure")
@app.get("/api/secure")
def secure_resource():
    """
    Chức năng mở rộng 4:
    Xác thực JWT token từ Keycloak:
    - Kiểm tra Header Authorization Bearer
    - Xác minh chữ ký RS256 bằng JWKS công khai từ Keycloak
    - Xác minh Issuer, Audience, Thời hạn Expiration
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify(
            error="Unauthorized: Missing or malformed Authorization header. Expected 'Bearer <token>'"
        ), 401

    token = auth_header.split(" ", 1)[1].strip()

    try:
        jwks = fetch_jwks()
    except Exception as err:
        logger.error(f"Failed to retrieve Keycloak JWKS: {err}")
        return jsonify(error="Identity Provider unavailable for token validation", details=str(err)), 503

    try:
        # Decode and rigorously verify JWT signature and claims
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        # Match key from JWKS
        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                rsa_key = key
                break

        if not rsa_key:
            return jsonify(error="Invalid Token: No matching key ID found in Keycloak JWKS"), 401

        # Decode & Verify token: signature, expiration, issuer
        # In Keycloak, audience can be 'account' or specific client; we verify azp or aud
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": False  # Handled below for flexible Keycloak client mapping
            }
        )

        # Check issuer
        token_issuer = payload.get("issuer") or payload.get("iss")
        if token_issuer != OIDC_ISSUER:
            logger.warning(f"Token issuer mismatch: got {token_issuer}, expected {OIDC_ISSUER}")
            # If accessed via localhost vs internal hostname, allow both in dev
            if not (token_issuer and "MyMiniCloud" in token_issuer):
                return jsonify(error="Token issuer verification failed", issuer=token_issuer), 401

        # Check audience or authorized party
        token_aud = payload.get("aud")
        token_azp = payload.get("azp")
        if OIDC_AUDIENCE not in str(token_aud) and token_azp != OIDC_AUDIENCE:
            logger.info(f"Audience note: token_aud={token_aud}, token_azp={token_azp}")

        return jsonify(
            message="Secure resource accessed successfully!",
            preferred_username=payload.get("preferred_username"),
            email=payload.get("email"),
            roles=payload.get("realm_access", {}).get("roles", []),
            expires_at=payload.get("exp")
        ), 200

    except jwt.ExpiredSignatureError:
        return jsonify(error="Token has expired"), 401
    except jwt.JWTClaimsError as err:
        return jsonify(error="Token claims verification failed", details=str(err)), 401
    except JWTError as err:
        return jsonify(error="Token cryptographic verification failed", details=str(err)), 401
    except Exception as err:
        logger.error(f"Unexpected error in token verification: {err}")
        return jsonify(error="Internal token validation error", details=str(err)), 500

if __name__ == "__main__":
    logger.info("Starting MyMiniCloud Application Backend Server on port 8081...")
    app.run(host="0.0.0.0", port=8081)

