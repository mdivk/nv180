c.JupyterHub.authenticator_class = 'ldapauthenticator.LDAPAuthenticator'
c.LDAPAuthenticator.server_address = 'nydc-dc01.xxxxxxx.pri'
c.LDAPAuthenticator.bind_dn_template = 'CN={username},OU=xxxxxxx Users,dc=xxxxxxx,dc=pri'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'CN'
c.LDAPAuthenticator.lookup_dn = True
c.LDAPAuthenticator.use_ssl = True
c.LDAPAuthenticator.lookup_dn_search_filter = '({login_attr}={login})'
c.LDAPAuthenticator.lookup_dn_search_user = 'CN=ldapbind2,OU=xxxxxxx Users (System),DC=xxxxxxx,DC=pri'
c.LDAPAuthenticator.lookup_dn_search_password = 'xxxxxxxxxxxxxxxxxx’
c.LDAPAuthenticator.user_attribute = 'sAMAccountName'
c.LDAPAuthenticator.user_search_base = 'ou=xxxxxxx Users,dc=xxxxxxx,dc=pri'
c.LDAPAuthenticator.user_search_filter = '(&(objectClass=person)(sAMAccountName={username}))'
c.LDAPAuthenticator.lookup_dn_user_dn_attribute = 'cn'
