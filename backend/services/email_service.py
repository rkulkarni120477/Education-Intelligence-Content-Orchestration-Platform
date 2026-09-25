"""Email service for sending notifications and password reset emails"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from config import get_settings
from datetime import datetime

logger = logging.getLogger(__name__)
settings = get_settings()


class EmailService:
    """Service for handling email operations"""

    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.sender_email = settings.SENDER_EMAIL
        self.sender_password = settings.SENDER_PASSWORD
        self.sender_name = settings.SENDER_NAME

    def send_email(self, recipient: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """
        Send an email to a recipient

        Args:
            recipient: Email address of recipient
            subject: Email subject
            html_content: HTML content of email
            text_content: Plain text fallback

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = recipient

            # Attach text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False

    def send_password_reset_email(self, email: str, full_name: str, reset_token: str, reset_url: str) -> bool:
        """Send password reset email"""
        subject = "Reset Your Academian Password"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #5B21B6 0%, #4C1D95 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .button {{ display: inline-block; margin: 20px 0; padding: 12px 30px; background: #5B21B6; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <p>Hi {full_name},</p>

                    <p>We received a request to reset the password for your Academian account. Click the button below to create a new password:</p>

                    <a href="{reset_url}?token={reset_token}" class="button">Reset Password</a>

                    <p>Or copy and paste this link in your browser:</p>
                    <p><small>{reset_url}?token={reset_token}</small></p>

                    <div class="warning">
                        <strong>⚠️ Important:</strong> This link will expire in 24 hours. If you didn't request this email, please ignore it.
                    </div>

                    <p>If you need help, please contact our support team at support@academian.com</p>

                    <p>Best regards,<br>The Academian Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Academian. All rights reserved.</p>
                    <p>This is an automated email. Please do not reply to this address.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request

        Hi {full_name},

        We received a request to reset the password for your Academian account.
        Click the link below to create a new password:

        {reset_url}?token={reset_token}

        This link will expire in 24 hours.

        If you didn't request this email, please ignore it.

        Best regards,
        The Academian Team
        """

        return self.send_email(email, subject, html_content, text_content)

    def send_welcome_email(self, email: str, full_name: str, verification_url: str) -> bool:
        """Send welcome email with verification link"""
        subject = "Welcome to Academian!"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #5B21B6 0%, #4C1D95 100%); color: white; padding: 20px; border-radius: 8px 8px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .button {{ display: inline-block; margin: 20px 0; padding: 12px 30px; background: #5B21B6; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .features {{ list-style: none; padding: 0; }}
                .features li {{ padding: 8px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Academian! 🎉</h1>
                </div>
                <div class="content">
                    <p>Hi {full_name},</p>

                    <p>Your account has been created successfully! Verify your email address to get started:</p>

                    <a href="{verification_url}" class="button">Verify Email</a>

                    <p><strong>What you can do:</strong></p>
                    <ul class="features">
                        <li>📚 Create and manage agentic workflows</li>
                        <li>🤖 Deploy AI agents for your organization</li>
                        <li>📊 Monitor agent performance and analytics</li>
                        <li>🔐 Manage API keys for integrations</li>
                        <li>⚙️ Customize your preferences and settings</li>
                    </ul>

                    <p>If you have any questions, check out our documentation or contact our support team.</p>

                    <p>Best regards,<br>The Academian Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Academian. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(email, subject, html_content)

    def send_workflow_notification(self, email: str, full_name: str, workflow_name: str, status: str, details: Optional[str] = None) -> bool:
        """Send workflow status notification"""
        status_emoji = {
            "started": "▶️",
            "completed": "✅",
            "failed": "❌"
        }.get(status, "📋")

        subject = f"Workflow {status.title()}: {workflow_name}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #5B21B6 0%, #4C1D95 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; margin-top: -8px; }}
                .status-box {{ padding: 15px; background: white; border-left: 4px; border-radius: 5px; margin: 15px 0; }}
                .status-started {{ border-left-color: #2563eb; }}
                .status-completed {{ border-left-color: #16a34a; }}
                .status-failed {{ border-left-color: #dc2626; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_emoji} Workflow {status.title()}</h1>
                </div>
                <div class="content">
                    <p>Hi {full_name},</p>

                    <div class="status-box status-{status}">
                        <p><strong>Workflow:</strong> {workflow_name}</p>
                        <p><strong>Status:</strong> {status.upper()}</p>
                        <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                        {f'<p><strong>Details:</strong> {details}</p>' if details else ''}
                    </div>

                    <p>Visit your dashboard to view more details and manage your workflows.</p>

                    <p>Best regards,<br>The Academian Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Academian. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(email, subject, html_content)


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
