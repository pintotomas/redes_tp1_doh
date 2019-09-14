import dns.resolver

# Resolve www.yahoo.com
result = dns.resolver.query('www.yahoo.com')
dns_records = [ip.address for ip in result]
#help(result.response)
#for answer in result.response.answer:
#    print(answer)
print(dns_records)