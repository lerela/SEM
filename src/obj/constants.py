# -*- coding: utf-8 -*-

"""
file: constants.py

Description: some useful constants that could be of some use in SEM and
beyond.

author: Yoann Dupont
copyright (c) 2016 Yoann Dupont - all rights reserved

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re

#
# Some useful regular expressions.
#

# URLs recognition. Validating URL is both hard and all urls may not be
# valid when analysing textual information. Hence, validity checking is
# kept to bare minimum, covering being more important.
protocol = "(?:http|ftp|news|nntp|telnet|gopher|wais|file|prospero)"
mailto   = "mailto"
url_body = "\S+[0-9A-Za-z/]"
url      = "<?(?:%s://|%s:|www\.)%s>?" %(protocol, mailto, url_body)
url_re   = re.compile(url)

# email addresses recognition. See URLs.
localpart_border = "[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~]"
localpart_inside = "[A-Za-z0-9!#$%&'*+\-/=?^_`{|}~.]"
localpart        = "%s%s*" %(localpart_border, localpart_inside)
subdomain_start  = "[A-Za-z]"
subdomain_inside = "[A-Za-z0-9\\-]"
subdomain_end    = "[A-Za-z0-9]"
subdomain        = "%s%s*%s" %(subdomain_start, subdomain_inside, subdomain_end)
domain           = "%s(?:\\.%s)*" %(subdomain, subdomain)
email_str        = "%s@%s" %(localpart, domain)
email_re         = re.compile(email_str)
