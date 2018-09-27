import os
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement, Comment
from .const import sfTypeSwitcher

class FiledPermissionUtil():
    _all_fields = []
    _all_sobjects = []
    _objects_dir = None

    def __init__(self, objects_dir):
        self._objects_dir = objects_dir

    def prettify(self, elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, encoding='UTF-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    # object xml content -> field map
    def get_fields_from_object_xml(self, object_name, contents):
        field_list = []
        contents = contents.replace('xmlns="http://soap.sforce.com/2006/04/metadata"', '')
        elem = ElementTree.fromstring(contents)
        for aField in elem.findall('fields'):
            fullName = aField.find('fullName').text if aField.find('fullName') is not None else ''
            label = aField.find('label').text if aField.find('label') is not None else ''
            field_type = aField.find('type').text if aField.find('type') is not None else ''
            is_required = aField.find('required').text == 'true' if aField.find('required') is not None else False
            if not fullName or not label or field_type == 'MasterDetail' or is_required:
                continue
            myField = {
                'key' : object_name + '.' + fullName,
                'object_name' : object_name,
                'fullName' : fullName,
                'label' : label,
                'type' : field_type,
                'formula' : aField.find('formula').text if aField.find('formula') is not None else ''
            }
            field_list.append(myField)
        return field_list

    def load_all_fields(self):
        self._all_fields = []
        self._all_sobjects = []
        for file in os.listdir(self._objects_dir):
            if not os.path.isdir(file):
                if file.endswith('object'):
                    object_name, file_extension = os.path.splitext(file)
                    full_path = os.path.join(self._objects_dir, file)
                    self._all_sobjects.append(object_name)
                    xml_content = ''
                    with open(full_path, "r", encoding='utf-8') as fp:
                        xml_content = fp.read()
                    if xml_content:
                        self._all_fields.extend(self.get_fields_from_object_xml(object_name, xml_content))
        return self._all_fields
    
    def get_all_fields(self):
        if len(self._all_fields) > 0:
            return self._all_fields
        else:
            return self.load_all_fields()

    # build sfdc fieldPermission
    def get_fieldPermission(self, permission_name = '', is_all_sobject_permission = False, sel_field_list = None):
        print(is_all_sobject_permission)
        all_fields = self.get_all_fields()
        top = Element('PermissionSet', {"xmlns": "http://soap.sforce.com/2006/04/metadata"})
        objects_permission = []
        for aField in all_fields:
            if sel_field_list and aField['key'] in sel_field_list or not sel_field_list:
                types = SubElement(top, 'fieldPermissions')
                editable = SubElement(types, 'editable')
                if aField['formula']:
                    editable.text = 'false'
                else:
                    editable.text = 'true'
                field = SubElement(types, 'field')
                field.text = aField['key']
                readable = SubElement(types, 'readable')
                readable.text = 'true'

                if not aField['object_name'] in objects_permission:
                    objects_permission.append(aField['object_name'])
        
        do_with_sobjects = self._all_sobjects if is_all_sobject_permission else objects_permission
        for aObj in do_with_sobjects:
            objectPermissions = SubElement(top, 'objectPermissions')
            allowCreate = SubElement(objectPermissions, 'allowCreate')
            allowCreate.text = 'true'
            allowDelete = SubElement(objectPermissions, 'allowDelete')
            allowDelete.text = 'true'
            allowEdit = SubElement(objectPermissions, 'allowEdit')
            allowEdit.text = 'true'
            allowRead = SubElement(objectPermissions, 'allowRead')
            allowRead.text = 'true'
            modifyAllRecords = SubElement(objectPermissions, 'modifyAllRecords')
            modifyAllRecords.text = 'true'
            aObject = SubElement(objectPermissions, 'object')
            aObject.text = aObj
            viewAllRecords = SubElement(objectPermissions, 'viewAllRecords')
            viewAllRecords.text = 'true'

        hasActivationRequired = SubElement(top, 'hasActivationRequired')
        hasActivationRequired.text = 'false'
        label = SubElement(top, 'label')
        label.text = permission_name
        license = SubElement(top, 'license')
        license.text = 'Salesforce'

        return self.prettify(top)