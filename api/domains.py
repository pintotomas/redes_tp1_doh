from flask import abort, make_response
import dns.resolver
import os
import json

# Data to serve with our API
domains = {
    #'fi.uba.ar': DomainInfo(['157.92.49.38'], False),
}

class DomainInfo:

    def __init__(self, ip_array, custom):
        self.ip_list = cycle(ip_array)
        self.custom = custom

    def change_ips(self, ip_array, custom):
        self.ip_list = cycle(ip_array)
        self.custom = custom

    def get_ip(self):
        return next(self.ip_list)

    def is_custom(self):
        return self.custom

def obtain_ip(domain_name):

  if domain_name in domains:
    domain_info = domains[domain_name]

    ip_address = domain_info.get_ip()
    is_custom = domain_info.is_custom()
    response = {'domain': domain_name, 'ip': ip_address, 'custom': is_custom}

    return make_response(json.dumps(response), 200)
    
  try:

    result = dns.resolver.query(domain_name)
    ips = [ip.address for ip in result]
    domain_info = DomainInfo(ips, False)
    domains[domain_name] = domain_info

    ip_address = domain_info.get_ip()
    is_custom = domain_info.is_custom()
    response = {'domain': domain_name, 'ip': ip_address, 'custom': is_custom}

    return make_response(json.dumps(response), 200)

  except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
    response = {'error': 'domain not found'}
    return make_response(json.dumps(response), 404)
  except (dns.exception.Timeout):
    response = {'error': 'The DNS operation timed out'}
    return make_response(json.dumps(response), 504)
  

def add_custom_domain(**kwargs):

    domain_info = kwargs.get('body')
    domain = domain_info.get('domain')
    ip = domain_info.get('ip')

    if domain in domains and domains[domain].is_custom():
        response = {"error": "custom domain already exists"}
        return make_response(json.dumps(response), 400)

    if not domain or not ip:
        response = {"error": "payload is inalid"}
        return make_response(json.dumps(response), 400)

    domains[domain] = DomainInfo([ip], True)
    response =   {"domain": domain, "ip": ip, "custom": True}
    return make_response(json.dumps(response), 201)
        
def edit_domain(**kwargs):
    domain_info = kwargs.get('body')
    if 'domain' not in domain_info or 'ip' not in domain_info:
        response = {"error": "payload is invalid"}
        return make_response(json.dumps(response), 400)

    domain = domain_info.get('domain')
    ip = domain_info.get('ip')

    if domain not in domains:
        response = response = {"error": "domain not found"}
        return make_response(json.dumps(response), 404)
    
    domains[domain].change_ips([ip], True)
    
    response =   {"domain": domain, "ip": ip, "custom": True}
    return make_response(json.dumps(response), 200)

def delete_domain(domain_name):
    if domain_name not in domains:
        response = {"error": "domain not found"}
        return make_response(json.dumps(response), 404)
    del domains[domain_name]
    response = {"domain": domain_name}
    return make_response(json.dumps(response), 200)

from itertools import cycle

def get_domains(**kwargs):

    domain_name = kwargs['domain_name'] if 'domain_name' in kwargs else ''
    items = [{"domain":k, "ip": v.get_ip(), "custom": v.is_custom()} for k, v in domains.items() if domain_name in k and v.is_custom()]
    
    return make_response({"items":items}, 200)

