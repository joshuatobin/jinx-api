from django.contrib.auth.backends import RemoteUserBackend
import settings as s
import ldap

class LDAPRemoteUserBackend(RemoteUserBackend):
	""" RemoteUserBackend for checking user/pass against REMOTE_USER
	and putting users in groups based on LDAP

	The following settings are required in settings.py:
	LDAP_SERVER='ldap://ldap.example.com'
	LDAP_SEARCH_TREE='ou=groups,dc=example,dc=com'
	LDAP_FILTER='(cn=example-django-group)'
	LDAP_FIELD='memberUid'
	"""
	
	def clean_username(self,username):
		"""Map REMOTE_USER to a django user. 
		In this case, REMOTE_USER is set by apache after 
		authenticating a kerberos user. REMOTE_USER
		is supplied with the kerberos domain appended 'eg user@domain', 
		this method strips the '@domain' section."""
		clean_username=username.split('@')[0]
		return clean_username

	def configure_user(self,user):
		"""Set user groups and privs. 
		This method is called the first time a non-django user logs in.
		A user is created in the django database, this method
		adds the new user to the appropriate groups, and 
		sets privs. """

		# Add all remote users to a group
		# user.groups.add(s.ALL_USERS_GROUP)

		# All remote users are staff - so they can access the admin interface
		user.is_staff=True

                # To determine if the user is to have further priviledges
		# we consult LDAP
		l = ldap.initialize(s.LDAP_SERVER)

                # bind
                l.bind_s(s.LDAP_BIND_DN, s.LDAP_PASSWD)

                ops = l.search_s(s.LDAP_SEARCH_TREE, ldap.SCOPE_SUBTREE, '(cn=ops)')[0][1]['memberUid']

		# close LDAP Connection
		l.unbind()

                # We need to set superuser when the database is being seeded. If we don't set superuser
                # then we're locked out of the admin interface. 
                if user.username in ops:
                        user.is_superuser=True
                user.save()

