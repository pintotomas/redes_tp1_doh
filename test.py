import dns.resolver

def resolve(domain):
	resolveList = []
	resolver = dns.resolver.Resolver(); #create a new instance named Resolver
	answer = resolver.query(domain).result.answer;
	return help(answer)
	#y=0
	#for rData in answer: 
#		resolveList.append(rData)
#		++y        
#	return resolveList

domainName = "www.yahoo.com"
queryResult = resolve(domainName);
for result in queryResult:
    print(queryResult[0])