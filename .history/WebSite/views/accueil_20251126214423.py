from django.contrib import messages
from django.core.mail import send_mail,EmailMessage
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.shortcuts import render 
from WebSTE.forms import contactForms

def home (request):

    return render (request, 'pages/accueil.html')

def service (request):

    return render (request,'pages/service.html')


def apropos (request):

    return render (request , 'pages/apropos.html')


def contact(request):

    form=contactForms()
    if request.method == 'POST':
        form = contactForms(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            countrycode = form.cleaned_data['countrycode']
            
            email_subject = f"Réception de mail d'un visiteur pour une demande de contact"
            email_body_html = render_to_string('pages/contact_email.html', {
                'email': email,
                'message': message,
                'phone': phone,
                'subject': subject,
                'name': name,
                'countrycode': countrycode
            })

            try:
                connection = get_connection()
                connection.open()
                email_message = EmailMessage(
                    email_subject,
                    email_body_html,
                    email,
                    ['ibrahimkabore025@gmail.com', ],
                    connection=connection,
                )
                email_message.content_subtype = 'html'
                email_message.send(fail_silently=False)
                messages.success(request, f"Merci pour votre message . Nous vous contacterons bientôt.")
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de l'envoi du message : {e}")
            finally:
                connection.close()
            return redirect('Contact')

    return render (request , 'pages/contact.html')