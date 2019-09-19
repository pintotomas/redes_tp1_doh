from flask import abort, make_response
import dns.resolver
import os
import json
# Data to serve with our API
domains = {
    #'fi.uba.ar': DomainInfo(['157.92.49.38'], False),
}


# Autor: https://github.com/vprusso/youtube_tutorials/blob/master/data_structures/linked_list/circular_linked_list/circular_linked_list_insert.py
# Cambios: Agregue un método get_next a la lista circular.

class Node(object):

  def __init__ (self, d, n = None):
    self.data = d
    self.next_node = n

  def get_next (self):
    return self.next_node

  def set_next (self, n):
    self.next_node = n
    
  def get_data (self):
    return self.data

  def set_data (self, d):
    self.data = d
    
  def to_string (self):
    return str(self.data)

class CircularLinkedList (object):

  def __init__ (self, r = None):
    self.root = r
    self.size = 0
    self.actual_node = r

  def add_many(self, list):
    for element in list:
      self.add(element)

  def get_next(self):
    if self.get_size() == 0:
      return ""
    actual_value =  self.actual_node.to_string()
    self.actual_node = self.actual_node.get_next()
    return actual_value

  def get_size (self):
    return self.size

  def add (self, d):
    if self.get_size() == 0:
      self.root = Node(d)
      self.root.set_next(self.root)
      self.actual_node = self.root
    else:
      new_node = Node (d, self.root.get_next())
      self.root.set_next(new_node)
    self.size += 1

  def remove (self, d):
    this_node = self.root
    prev_node = None

    while True:
      if this_node.get_data() == d: # found
        if prev_node is not None:
          prev_node.set_next(this_node.get_next())
        else:
          while this_node.get_next() != self.root:
            this_node = this_node.get_next()
          this_node.set_next(self.root.get_next())
          self.root = self.root.get_next()
        self.size -= 1
        return True     # data removed
      elif this_node.get_next() == self.root:
        return False  # data not found
      prev_node = this_node
      this_node = this_node.get_next()

  def find (self, d):
    this_node = self.root
    while True:
      if this_node.get_data() == d:
        return d
      elif this_node.get_next() == self.root:
        return False
      this_node = this_node.get_next()
    
  def print_list (self):
    print ("Print List..........")
    if self.root is None:
      return
    this_node = self.root
    print (this_node.to_string())
    while this_node.get_next() != self.root:
      this_node = this_node.get_next()
      print (this_node.to_string())

class DomainInfo:

    def __init__(self, ip_array, custom):
        new_circular_list = CircularLinkedList()
        new_circular_list.add_many(ip_array)
        self.ip_list = new_circular_list
        self.custom = custom

    def change_ips(self, ip_array, custom):
        new_circular_list = CircularLinkedList()
        new_circular_list.add_many(ip_array)
        self.ip_list = new_circular_list
        self.custom = custom

    def get_ip(self):
        return self.ip_list.get_next()

    def is_custom(self):
        return self.custom

    def update_ips(self, ip_array):
        
        #Primero chequeo cuales ips de ip_array no estan siendo tenidas en cuenta:
        for ip in ip_array:
          if not(self.ip_list.find(ip)):
            self.ip_array.add(ip)

        #Luego chequeo cuales debo descartar:
        ips_a_eliminar = []
        for x in range(self.ip_list.get_size()):
          ip_actual = self.ip_list.get_next()
          if ip_actual not in ip_array:
            ips_a_eliminar.append(ip_actual)

        #Finalmente, las elimino
        for ip in ips_a_eliminar:
          self.ip_list.remove(ip)

def search_for_ips(domain_name):

    result = dns.resolver.query(domain_name)
    ips = [ip.address for ip in result]
    return ips

def obtain_ip(domain_name):

  if domain_name in domains:
    domain_info = domains[domain_name]  
    is_custom = domain_info.is_custom()
    if not(is_custom): # Si no es custom y fue guardada anteriormente deberia actualizar las ips 
        ips = search_for_ips(domain_name)
        domain_info.update_ips(ips)

    ip_address = domain_info.get_ip()
    response = {'domain': domain_name, 'ip': ip_address, 'custom': is_custom}

    return make_response(json.dumps(response), 200)
    
  try:

    ips = search_for_ips(domain_name)
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
        response = {"error": "payload is invalid"}
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

    if domain not in domains or not(domains[domain].is_custom()):
        response = response = {"error": "custom domain not found"}
        return make_response(json.dumps(response), 404)
    
    domains[domain].change_ips([ip], True)
    
    response =   {"domain": domain, "ip": ip, "custom": True}
    return make_response(json.dumps(response), 200)

def delete_domain(domain_name):
    if domain_name not in domains or not(domains[domain_name].is_custom()):
        response = {"error": "custom domain not found"}
        return make_response(json.dumps(response), 404)

    del domains[domain_name]
    response = {"domain": domain_name}
    return make_response(json.dumps(response), 200)

from itertools import cycle

def get_domains(**kwargs):

    domain_name = kwargs['domain_name'] if 'domain_name' in kwargs else ''
    items = [{"domain":k, "ip": v.get_ip(), "custom": v.is_custom()} for k, v in domains.items() if domain_name in k and v.is_custom()]
    
    return make_response({"items":items}, 200)

