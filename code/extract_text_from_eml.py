#!/usr/bin/python3

import email
from email import policy
from email.parser import BytesParser

# Function to extract the body from each individual email
def extract_email_body_from_message(message):
    if message.is_multipart():
        for part in message.iter_parts():
            if part.get_content_type() == "text/plain":
                charset = part.get_content_charset() or 'utf-8'  # Fallback to 'utf-8' if charset is None
                return part.get_payload(decode=True).decode(charset)
    else:
        charset = message.get_content_charset() or 'utf-8'  # Fallback to 'utf-8' if charset is None
        return message.get_payload(decode=True).decode(charset)

# Function to handle multiple emails in a single file and save output to a file
def extract_emails_from_file(eml_file_path, output_file_path):
    email_bodies = []
    
    with open(eml_file_path, 'rb') as f:
        content = f.read()

    # Split on "From " which typically separates emails in concatenated files
    email_messages = content.split(b'\n\nFrom ')
    
    # Parse each email separately
    for idx, raw_email in enumerate(email_messages):
        if idx == 0:
            # The first part won't start with "From " so we don't strip it
            raw_email = raw_email
        else:
            # The following parts start with "From " so we prepend it
            raw_email = b'From ' + raw_email

        # Parse the raw email
        try:
            msg = BytesParser(policy=policy.default).parsebytes(raw_email)
            # Extract the body
            email_body = extract_email_body_from_message(msg)
            if email_body:
                email_bodies.append(f"Email {idx + 1}:\n{email_body}\n{'-' * 80}\n")
        except Exception as e:
            print(f"Failed to parse email {idx + 1}: {e}")
            continue
    
    # Save the extracted email bodies to the output file
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        for body in email_bodies:
            output_file.write(body)

    print(f"Extracted email content has been saved to {output_file_path}")

# Example usage
eml_file = 'path_to_your_email_file.eml'
output_file = 'output_emails.txt'  # Specify the output file path
extract_emails_from_file(eml_file, output_file)

