#!/usr/bin/env python
# -*- coding: utf-8 -*-

import dns.resolver
import json
from collections import OrderedDict
from app.models import DnsCache, Pool


def get_resolvers():
    with open('dns-servers.json', 'r') as f:
        servers = json.load(f)

    resolvers = []
    for ns in servers:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [ns['ip']]
        resolvers.append(resolver)
    return resolvers


def get_ips_for_domain(domain):
    """
    Returns a list of IPv4 addresses for the given domain.
    :param domain:
    :return:
    """
    result = set()
    for resolver in get_resolvers():
        try:
            ips = resolver.query(domain, 'A')
        except dns.exception.DNSException:
            print("Could not resolve '%s' using nameserver '%s'" % (domain, str(resolver.nameservers[0])))
        result.update([str(ip) for ip in ips])
    return result


def retrieve_domains():
    """
    Returns the set of distinct domains from `pools.csv`.
    :return:
    """
    pools = Pool.read_pools('pools.csv', cached_only=False)
    return OrderedDict((x, True) for x in [p.domain for p in pools]).keys()


def update_dns():
    print("Retrieving DNS updates...")
    domains = retrieve_domains()
    for domain in domains:
        print(domain, end='')
        ips = ','.join(get_ips_for_domain(domain))
        dns = DnsCache(domain=domain, ips=ips)
        stored_dns = DnsCache.get_by_domain(domain)
        if stored_dns is None or stored_dns != dns:
            dns.save()
            print(' ... added', end='')
        print()


if __name__ == '__main__':
    update_dns()
