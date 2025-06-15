# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from telegram import Bot
from bot.config import BOT_TOKEN, PLANS
from bot.subscriber_manager import subscriber_manager
from bot.payment_links import payment_generator
import logging

logger = logging.getLogger(__name__)

async def handle_payment_webhook(request: Request):
    """Handle payment confirmation webhook"""
    try:
        data = await request.json()
        
        # Extract payment info (adjust based on your payment provider)
        transaction_id = data.get("transaction_id")
        user_id = data.get("user_id")
        metadata = data.get("metadata", {})
        plan_id = metadata.get("plan_id")
        status = data.get("status")
        
        if status == "completed" and transaction_id:
            # Verify payment link
            payment_info = payment_generator.verify_payment_link(transaction_id)
            
            if payment_info:
                # Look up plan name using identifier
                plan_info = PLANS.get(plan_id)
                if not plan_info:
                    raise ValueError(f"Unknown plan id: {plan_id}")
                plan_name = plan_info["name"]

                # Mark payment as completed
                payment_generator.mark_payment_completed(user_id, plan_name)

                # Add subscriber
                success = subscriber_manager.add_subscriber(
                    user_id=user_id,
                    plan_name=plan_name,
                    transaction_id=transaction_id
                )
                
                if success:
                    # Send confirmation to user
                    bot = Bot(token=BOT_TOKEN)
                    await bot.send_message(
                        chat_id=user_id,
                        text=f"✅ Payment confirmed! Your {plan_name} subscription is now active."
                    )
                    
                    logger.info(f"Payment confirmed for user {user_id}, plan {plan_name}")
                    return {"status": "success"}
        
        return {"status": "ignored"}
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
