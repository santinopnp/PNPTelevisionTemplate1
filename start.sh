#!/bin/bash
echo "Starting Telegram Bot Services..."
echo "Environment Variables:"
echo "DATABASE_URL: ${DATABASE_URL:0:20}..."  # Show first 20 chars for security
echo "BOT_TOKEN: ${BOT_TOKEN:0:10}..."
echo "PORT: $PORT"
echo "ADMIN_PORT: $ADMIN_PORT"

# Start supervisor
exec supervisord -c supervisord.conf
