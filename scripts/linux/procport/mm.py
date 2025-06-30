#!/usr/bin/python3
import re, subprocess, datetime, smtplib, ssl, argparse
from email.mime.text import MIMEText
from email.message import EmailMessage

email_regex = r"[A-Za-z0-9]+@(gmail|live|icloud|bebop831)+\.(com|org|net|io)+$" #regex pattern matching for email
DEFAULT_CREDS_FILE = ".creds"
DEFAULT_SMTP_SERVER="smtp.mailbox.org"

def send_mail(from_addr: str, to_addr : str, econ : smtplib.SMTP_SSL, msg: str):
	#prgrp for command
	cmd_out = check_host([], "fwupd")

	right_now = datetime.datetime.now(datetime.timezone.utc)
	
	msg_tmp = EmailMessage()
	msg_tmp['Subject'] = f"procport-{right_now}"
	msg_tmp['From'] = from_addr
	msg_tmp['CC'] = ""
	msg_tmp['To'] = to_addr
	msg_tmp.set_content("<h1>Can we render HTML in an email?</h1>\n" + cmd_out, subtype='html')

	econ.set_debuglevel(True)
	print(msg_tmp.as_string())
	econ.sendmail(from_addr, to_addr, msg_tmp.as_string())


def check_host(hosts : list, proc : str):
	#shell=False subprocess, therefor no $PATH
	email_proc = subprocess.run(["/usr/bin/pgrep", "-ax", proc], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False, shell=False)
	cmd_out = email_proc.stdout

	return cmd_out

def parse_emails(email_list) -> list[str]:
	parsed_list = []
	for current_email in email_list:
		if re.match(email_regex, current_email):
			parsed_list.append(current_email.strip())
	return parsed_list


def main():

	try:
		parser = argparse.ArgumentParser(description="Tool for watching and reporting on live processes")
		parser.add_argument("email", help="Report recipient address")
		parser.add_argument("host_file", help="File containing line seperated host FQDNs that will be queried")
		parser.add_argument("-c", "--creds", type=str, help="Path to file containing EMAIL:APP_PASSWORD (Default: .creds)")

		args = parser.parse_args()
		parsed_emails = parse_emails(args.email.split(','))
		print(f"Emails found: {parsed_emails}")

		with open(args.creds if args.creds else DEFAULT_CREDS_FILE, "r") as creds_fd:
			creds = creds_fd.read().split(':')            #email:pass
			sender_email, pwd = creds[0].strip(), creds[1].strip()
			email_con = smtplib.SMTP_SSL("smtp.mailbox.org")
			email_con.login(sender_email, pwd)

		with open(args.host_file, 'r') as hosts_fd:
			hosts = hosts_fd.readlines()
			check_host(hosts, "")
			for email in parsed_emails:
				send_mail(
					from_addr=sender_email,
					to_addr=email,
					msg="firefox",
					econ=email_con
				)
	except Exception as e:
		print(e)

main()
