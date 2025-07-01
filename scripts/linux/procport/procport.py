#!/usr/bin/python3
import re, subprocess, datetime, smtplib, argparse, dotenv, os
from email.message import EmailMessage
from smtplib import SMTPAuthenticationError
from jinja2 import Environment, FileSystemLoader

email_regex = r"[A-Za-z0-9]+@[A-Za-z0-9]+\.[a-z]+$" #regex pattern matching for email
DEFAULT_CREDS_FILE = ".creds"
right_now = lambda : datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%m-%d-%Y %H:%M:%S")



#prgrp for command
def send_mail(from_addr: str, to_addr : str, econ : smtplib.SMTP_SSL, msg: str, debug : bool = False):

	msg_tmp = EmailMessage()
	msg_tmp['Subject'] = f"procport-{right_now()}"
	msg_tmp['From'] = from_addr
	msg_tmp['CC'] = ""
	msg_tmp['To'] = to_addr
	msg_tmp.set_content(msg, subtype='html')

	econ.set_debuglevel(debug)
	if(debug):
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
		parser = argparse.ArgumentParser(description="pgreps a list of hosts and emails a below average report")
		parser.add_argument("email", help="Single or Comma seperated list of email addresses that will recieve below average report")
		parser.add_argument("host_file", help="File containing line seperated host FQDNs that will be queried")
		parser.add_argument("-c", "--creds", type=str, help="Path to file containing EMAIL:APP_PASSWORD (Default: .creds)", default=DEFAULT_CREDS_FILE)
		parser.add_argument("-v", "--verbose", action="store_true", help="Print debug messageing", default=False)

		env = Environment(loader=FileSystemLoader("templates/"))
		email_template = env.get_template("report_template_1.html.j2")
		args = parser.parse_args()
		parsed_emails = parse_emails(args.email.split(','))
		
		
		login_email = os.environ.get("PMAIL")
		passwd = os.environ.get("PPASS")
		smtp_server = os.environ.get("SMTP_SERVER")

		if not login_email or not passwd or not smtp_server:
			dotenv.load_dotenv()
			login_email = os.environ.get("PMAIL")
			passwd = os.environ.get("PPASS")
			smtp_server = os.environ.get("SMTP_SERVER")


		print("Emails found:", parsed_emails)
		print("SMTP Server:", smtp_server)


		email_con = smtplib.SMTP_SSL(smtp_server)
		email_con.login(login_email, passwd)

		with open(args.host_file, 'r') as hosts_fd:
			hosts = hosts_fd.readlines()
# 			cmd_out = check_host(hosts, "")
			for email in parsed_emails:
				send_mail(
					from_addr=login_email,
					to_addr=email,
					msg=email_template.render(curr_time=right_now(), hosts=[
						{"fqdn" : "ubuntu-lax4.local", "proc" : {"name" : "thunderbird", "is_running" : True} },
						{"fqdn" : "ubuntu-ny2.local", "proc" : {"name" : "firefox", "is_running" : False} 
	   				}]),
					econ=email_con,
					debug=args.verbose
				)

	except SMTPAuthenticationError as auth_err:
		print("Authentication Failed...")
		if args.verbose:
			print(auth_err)


	except Exception as e:
		print(e)



main()
