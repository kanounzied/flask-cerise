import getpass
import smtplib
import ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sendConfirm(receiver_mail,link):
    port = 465  # For SSL
    password = "Ds3X8afA"  # getpass.getpass("Type your password : ")
    sender_mail = "artzy.proj@gmail.com"
    # receiver_mail = "zied.kanoun6@gmail.com"
    subject = "verification mail"

    message = MIMEMultipart("alternative")
    message['Subject'] = subject
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message["Bcc"] = receiver_mail  # Recommended for mass emails

    # Create the plain-text and HTML version of your message

    plain_text = """\
    hi,
    this message is for test,
    to send contract ntification"""
    html = """\
    <html>
        <body style='color: black;'>
            <h1>Hello, you're a click away</h1><br>
            <p>Hit the button to verify your email</p>
            <a href='"""+link+"""' style='border: 1px solid #e81b2e;
                    border-radius: 4px;
                    padding: 10px 25px;
                    color: #e81b2e;
                    margin: 50px 0;
                    background-color: #ffdfe4;'>Verify my email</a>
            <p>    </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects

    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    message.attach(part1)
    message.attach(part2)

    ############### attachment part ##################

    # filename = "demande_de_stage.pdf"  # In same directory as script
    #
    # # Open PDF file in binary mode
    # with open(filename, "rb") as attachment:
    #     # Add file as application/octet-stream
    #     # Email client can usually download this automatically as attachment
    #     part = MIMEBase("application", "octet-stream")
    #     part.set_payload(attachment.read())
    #
    # # Encode file in ASCII characters to send by email
    # encoders.encode_base64(part)
    #
    # # Add header as key/value pair to attachment part
    # part.add_header(
    #     "Content-Disposition",
    #     f"attachment; filename= {filename}",
    # )
    #
    # # Add attachment to message and convert message to string
    # message.attach(part)

    ############ end of attachment part ###############

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("artzy.proj@gmail.com", password)
        # print('connected!')
        server.sendmail(sender_mail, receiver_mail, message.as_string())
        # print('message sent!')
def sendCode(receiver_mail,code):
    port = 465  # For SSL
    password = "Ds3X8afA"  # getpass.getpass("Type your password : ")
    sender_mail = "artzy.proj@gmail.com"
    # receiver_mail = "zied.kanoun6@gmail.com"
    subject = "verification mail"

    message = MIMEMultipart("alternative")
    message['Subject'] = subject
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message["Bcc"] = receiver_mail  # Recommended for mass emails

    # Create the plain-text and HTML version of your message

    plain_text = """\
    hi,
    this message is for test,
    to send contract ntification"""
    html = """\
    <html>
        <body style='color: black;'>
            <h1>Hello, here's a code</h1><br>
            <p>retype this code in its place and reinitialize your password</p>
            <a href='#'>"""+str(code)+"""</a>
            <p>    </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects

    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    message.attach(part1)
    message.attach(part2)

    ############### attachment part ##################

    # filename = "demande_de_stage.pdf"  # In same directory as script
    #
    # # Open PDF file in binary mode
    # with open(filename, "rb") as attachment:
    #     # Add file as application/octet-stream
    #     # Email client can usually download this automatically as attachment
    #     part = MIMEBase("application", "octet-stream")
    #     part.set_payload(attachment.read())
    #
    # # Encode file in ASCII characters to send by email
    # encoders.encode_base64(part)
    #
    # # Add header as key/value pair to attachment part
    # part.add_header(
    #     "Content-Disposition",
    #     f"attachment; filename= {filename}",
    # )
    #
    # # Add attachment to message and convert message to string
    # message.attach(part)

    ############ end of attachment part ###############

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("artzy.proj@gmail.com", password)
        # print('connected!')
        server.sendmail(sender_mail, receiver_mail, message.as_string())
        # print('message sent!')


def sendPDF(receiver_mail,pdf, text):
    port = 465  # For SSL
    password = "Ds3X8afA"  # getpass.getpass("Type your password : ")
    sender_mail = "artzy.proj@gmail.com"
    # receiver_mail = "zied.kanoun6@gmail.com"
    subject = "contrat assurence immobiliere"

    message = MIMEMultipart("alternative")
    message['Subject'] = subject
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message["Bcc"] = receiver_mail  # Recommended for mass emails

    # Create the plain-text and HTML version of your message

    plain_text = """\
    hi,
    this message is for test,
    to send contract ntification"""
    # text assosciation : this is the contract of the client named client with the id id : this contract is (still not)
    # paid
    # text client : the contract is ready now and waiting to be paid if you want to modify it just log in and choose
    # your contract if you have more than one
    html = """\
    <html>
        <body style='color: black;'>
            <h1>Hello , the contract is here! </h1><br>
            <p>"""+text+"""</p>
            <p>    </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects

    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    message.attach(part1)
    message.attach(part2)

    ############### attachment part ##################

    # filename = pdf_name  # In same directory as script

    # Open PDF file in binary mode
    # with open(filename, "rb") as attachment:
    #     # Add file as application/octet-stream
    #     # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    #     # print(attachment.read())
    part.set_payload(pdf)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {'contrat.pdf'}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)

    ############ end of attachment part ###############

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("artzy.proj@gmail.com", password)
        # print('connected!')
        server.sendmail(sender_mail, receiver_mail, message.as_string())
        # print('message sent!')
def sendPDFv(receiver_mail,pdf, text):
    port = 465  # For SSL
    password = "Ds3X8afA"  # getpass.getpass("Type your password : ")
    sender_mail = "artzy.proj@gmail.com"
    # receiver_mail = "zied.kanoun6@gmail.com"
    subject = "contrat assurence auto"

    message = MIMEMultipart("alternative")
    message['Subject'] = subject
    message['From'] = sender_mail
    message['To'] = receiver_mail
    message["Bcc"] = receiver_mail  # Recommended for mass emails

    # Create the plain-text and HTML version of your message

    plain_text = """\
    hi,
    this message is for test,
    to send contract ntification"""
    # text assosciation : this is the contract of the client named client with the id id : this contract is (still not)
    # paid
    # text client : the contract is ready now and waiting to be paid if you want to modify it just log in and choose
    # your contract if you have more than one
    html = """\
    <html>
        <body style='color: black;'>
            <h1>Hello , the contract is here! </h1><br>
            <p>"""+text+"""</p>
            <p>    </p>
        </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects

    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first

    message.attach(part1)
    message.attach(part2)

    ############### attachment part ##################

    # filename = pdf_name  # In same directory as script

    # Open PDF file in binary mode
    # with open(filename, "rb") as attachment:
    #     # Add file as application/octet-stream
    #     # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    #     # print(attachment.read())
    part.set_payload(pdf)

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {'contrat.pdf'}",
    )

    # Add attachment to message and convert message to string
    message.attach(part)

    ############ end of attachment part ###############

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login("artzy.proj@gmail.com", password)
        # print('connected!')
        server.sendmail(sender_mail, receiver_mail, message.as_string())
        # print('message sent!')