"""
Servicio de Emails - Gestión centralizada de envío de correos
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para enviar correos electrónicos usando templates"""
    
    @staticmethod
    def send_email(subject, template_name, context, recipient_list, from_email=None):
        """
        Método base para enviar correos usando templates HTML.
        Retorna True si se envió correctamente, False en caso de error.
        """
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        try:
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            msg.attach_alternative(html_content, "text/html")
            msg.encoding = 'utf-8'  # Forzar encoding UTF-8 para caracteres especiales
            msg.send()
            return True
        except Exception as e:
            import traceback
            logger.error(f"Error enviando correo a {recipient_list}: {e}")
            logger.error(traceback.format_exc())
            return False

    @staticmethod
    def send_verification_email(user, token, verification_url):
        """
        Envía el correo de verificación de cuenta al usuario.
        """
        subject = "Verifica tu cuenta en MultiTienda"
        context = {
            'user': user,
            'verification_url': verification_url,
        }
        return EmailService.send_email(
            subject,
            'appOnichan/emails/verification_email.html',
            context,
            [user.email]
        )

    @staticmethod
    def send_order_confirmation(order):
        """
        Envía el comprobante de compra al cliente.
        Usa contact_email del pedido o el email del usuario registrado.
        """
        subject = f"Confirmación de Pedido #{order.code}"
        context = {
            'order': order,
            'items': order.items.all(),
        }
        # Priorizar email del pedido, luego el del usuario
        recipient = order.contact_email or (order.user.email if order.user else None)
        
        if not recipient:
            logger.warning(f"No se pudo enviar confirmación de pedido {order.code}: Sin email de destinatario.")
            return False

        return EmailService.send_email(
            subject,
            'appOnichan/emails/order_confirmation.html',
            context,
            [recipient]
        )

    @staticmethod
    def send_marketing_email(subject, body_html, recipient_list):
        """
        Envía correos masivos de marketing.
        Nota: Para producción, considerar usar background tasks (Celery) o BCC.
        Actualmente envía individualmente usando una conexión única para mejor rendimiento.
        """
        
        from django.core.mail import get_connection
        
        connection = get_connection()
        messages = []
        
        # Preparar mensajes usando template de marketing
        for email in recipient_list:
            context = {'body': body_html}
            html_content = render_to_string('appOnichan/emails/marketing_email.html', context)
            text_content = strip_tags(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email], connection=connection)
            msg.attach_alternative(html_content, "text/html")
            messages.append(msg)
            
        return connection.send_messages(messages)
