import os
import email
from email import policy
from email.parser import BytesParser
import re

# Function to extract plain text content from mailbox file
def extract_and_group_emails_by_subject(mailbox_file):
    output_dir = "grouped_emails"
    os.makedirs(output_dir, exist_ok=True)

    # Dictionary to store content grouped by subject
    email_content_by_subject = {}

    # Initialize a list to store individual emails
    email_data = []
    current_email = []

    # Read the mailbox file line by line
    with open(mailbox_file, "rb") as f:
        for line in f:
            # Detect the start of a new email
            if line.startswith(b"From "):
                if current_email:
                    email_data.append(b"".join(current_email))
                    current_email = []
            current_email.append(line)
        
        # Add the last email if any
        if current_email:
            email_data.append(b"".join(current_email))

    # Process each email
    for i, eml in enumerate(email_data):
        try:
            # Parse the email
            msg = BytesParser(policy=policy.default).parsebytes(eml)

            # Extract and sanitize the subject
            subject = msg.get("Subject", "No Subject").strip()
            sanitized_subject = re.sub(r'[\/:*?"<>|]', "_", subject)

            # Extract the date
            date = msg.get("Date", "Unknown Date").strip()

            # Extract plain text content
            text_content = extract_text_from_email(msg)

            # Skip if no plain text content is found
            if not text_content.strip():
                print(f"No plain text content found in email {i}. Skipping...")
                continue

            # Prepare the entry with subject, date, and text content
            entry = f"Subject: {subject}\nDate: {date}\n\n{text_content}"

            # Append the entry to the corresponding subject in the dictionary
            if sanitized_subject in email_content_by_subject:
                email_content_by_subject[sanitized_subject] += "\n\n---\n\n" + entry
            else:
                email_content_by_subject[sanitized_subject] = entry

        except Exception as e:
            print(f"Failed to process email {i}: {e}")

    # Write grouped content to output files
    for subject, content in email_content_by_subject.items():
        output_file = os.path.join(output_dir, f"{subject}.txt")
        with open(output_file, "w", encoding="utf-8") as out_file:
            out_file.write(content)
        print(f"Grouped and saved: {output_file}")

# Helper function to extract plain text content from an email message
def extract_text_from_email(msg):
    text_content = ""

    # Walk through all parts of the email, including nested parts
    for part in msg.walk():
        # Check if the part is plain text and not an attachment
        content_disposition = part.get("Content-Disposition", "")
        if part.get_content_type() == "text/plain" and "attachment" not in content_disposition:
            try:
                text_content += part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
            except Exception as e:
                print(f"Failed to decode part: {e}")

    return text_content

if __name__ == "__main__":
    mailbox_file = "/mnt/data/mailbox.eml"  # Path to the mailbox file
    extract_and_group_emails_by_subject(mailbox_file)

