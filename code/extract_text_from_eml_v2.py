import os
import email
from email import policy
from email.parser import BytesParser
from collections import defaultdict

def extract_emails_from_eml(eml_file):
    emails = defaultdict(list)

    with open(eml_file, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

        subject = msg['subject']
        date = msg['date']
        body = msg.get_body(preferencelist=('plain')).get_content()

        # Store emails by subject
        emails[subject].append({
            'date': date,
            'body': body
        })

    return emails

def save_emails(emails):
    for subject, messages in emails.items():
        # Create a safe filename from the subject
        safe_subject = ''.join(c for c in subject if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{safe_subject}.txt"

        with open(filename, 'a') as f:
            for message in messages:
                f.write(f"Subject: {subject}\n")  # Include subject in the output
                f.write(f"Date: {message['date']}\n")
                f.write(f"Body:\n{message['body']}\n\n")

if __name__ == "__main__":
    eml_file = 'path_to_your_file.eml'  # Replace with your EML file path
    emails = extract_emails_from_eml(eml_file)
    save_emails(emails)

