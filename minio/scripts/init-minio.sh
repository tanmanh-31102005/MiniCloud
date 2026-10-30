#!/bin/sh
set -e

echo "Waiting for MinIO object-storage-server to be available..."
until (mc alias set myminio http://object-storage-server:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"); do
    echo "MinIO not ready yet, sleeping 2s..."
    sleep 2
done

echo "MinIO is ready. Creating required buckets..."
mc mb --ignore-existing myminio/"$MINIO_BUCKET_PROFILE"
mc mb --ignore-existing myminio/"$MINIO_BUCKET_DOCS"

echo "Setting public download policy on profile-pics bucket..."
mc anonymous set download myminio/"$MINIO_BUCKET_PROFILE"

if [ -f /data_sample/avatar.jpg ]; then
    echo "Uploading sample avatar.jpg to profile-pics..."
    mc cp /data_sample/avatar.jpg myminio/"$MINIO_BUCKET_PROFILE"/avatar.jpg
fi

if [ -f /data_sample/report.pdf ]; then
    echo "Uploading sample report.pdf to documents..."
    mc cp /data_sample/report.pdf myminio/"$MINIO_BUCKET_DOCS"/report.pdf
fi

echo "MinIO initialization completed successfully!"
mc ls myminio/"$MINIO_BUCKET_PROFILE"
mc ls myminio/"$MINIO_BUCKET_DOCS"

