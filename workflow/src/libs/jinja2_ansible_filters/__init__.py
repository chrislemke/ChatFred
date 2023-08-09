# (c) 2019, Nick Shobe <nickshobe@gmail.com>
# This code is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

from jinja2_ansible_filters.core_filters import FilterModule

from jinja2.ext import Extension

import warnings


class AnsibleCoreFiltersExtension(Extension):

    def __init__(self, environment):
        super().__init__(environment)
        filters = FilterModule().filters()
        for x in filters:
            if x in environment.filters:
                warnings.warn("Filter name collision detected changing "
                              "filter name to ans_{0} "
                              "to avoid clobbering".format(x),
                              RuntimeWarning)
                filters["ans_" + x] = filters[x]
                del filters[x]

        # Register provided filters
        environment.filters.update(filters)
