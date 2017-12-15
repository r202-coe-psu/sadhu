import ldap3
from flask import current_app


class LDAPClient:
    def __init__(self, name, password):
        self.server = ldap3.Server(current_app.config.get('LDAP_SERVER'))
        self.identifier = current_app.config.get('LDAP_IDENTIFIER')
        self.identifier_text = 'uid={name},{identifier}'.format(
                name=name,
                identifier=self.identifier)
        self.__name = name
        self.__password = password

        self.connection = ldap3.Connection(self.server,
                user=self.identifier_text,
                password=password)
    
    def authenticate(self):
        return self.connection.bind()

    def get_info(self):
        result = self.connection.search(self.identifier,
                    '(&(objectclass=person)(uid={}))'.format(self.__name),
                    attributes=['*'])
        if result: 
            return self.transpiler_entry(self.connection.entries[0])
        else:
            return None

    def transpiler_entry(self, entry):
        result = dict()
        attributes = dict(
                cn='display_name',
                personalID='personal_id',
                givenName='first_name',
                sn='last_name',
                employeeNumber='employee_number',
                mail='email',
                campusName='campus',
                departmentName='department',
                facultyName='faculty',
                o='university',
                uid='uid'
                )
        
        entry_dict = entry.entry_attributes_as_dict
        for k, v in attributes.items():
            if k in entry_dict:
                result[v] = entry_dict[k][0]

        return result
