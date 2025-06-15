# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from bot.config import BOT_TOKEN
from bot.subscriber_manager import subscriber_manager
from bot.payment_links import payment_generator
import logging

logger = logging.getLogger(__name__)

async def handle_payment_webhook(request: Request):
    """Handle payment confirmation webhook"""
    try:
        data = await request.json()
        
        # Extract payment info (adjust based on your payment provider)
        metadata = data.get("metadata", {})
        transaction_id = data.get("transaction_id") or metadata.get("tx")
        user_id = data.get("user_id") or metadata.get("user_id")
        plan_id = data.get("plan") or metadata.get("plan")
        status = data.get("status")
        
        if status == "completed" and transaction_id:
            # Verify payment link
            payment_info = payment_generator.verify_payment_link(transaction_id)
            
            if payment_info:
                # Mark payment as completed
                payment_generator.mark_payment_completed(user_id, plan_id)

                # Add subscriber
                success = await subscriber_manager.add_subscriber(
                    user_id=user_id,
                    plan_name=plan_id,
                    transaction_id=transaction_id
                )
                
                if success:
                    # Send confirmation to user
                    bot = Bot(token=BOT_TOKEN)
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Payment confirmed! Your {plan_id} subscription is now active."
                    )
                    
                    logger.info(f"Payment confirmed for user {user_id}, plan {plan_id}")
                    return {"status": "success"}
        
        return {"status": "ignored"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
