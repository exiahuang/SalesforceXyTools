import os,json
import shutil
import tempfile
import zipfile

class Template():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    template_folder = "metadata-templates"
    config_file = "package.json"

    def __init__(self):
        if is_installed_package(self.dir_path):
            self.root_path = os.path.join(tempfile.gettempdir(), "salesforcexytools", "templates")
            packageFile = os.path.dirname(self.dir_path)
            extract_template(packageFile)
        else:
            self.root_path = self.dir_path

    def load_config(self, type):
        config_path = os.path.join(self.root_path, self.template_folder, self.config_file)
        with open(config_path) as fp:
            templates_config = json.loads(fp.read())
        return templates_config[type]
    
    def load_config_dict(self, type):
        config = self.load_config(type)
        config_dict = {}
        for item in config:
            config_dict[item["name"]] = item 
        return config_dict
    
    def get(self, type, name):
        template_path = os.path.join(self.root_path, self.template_folder, type, name)
        print(template_path)
        with open(template_path) as fp:
            template = fp.read()
        return template

    def get_src(self, type, name, data):
        src = self.get(type, name)
        for key, value in data.items():
            if value:
                src = src.replace("{{ " + key + " }}", value)
        return src


class AntConfig():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    template_folder = "ant-templates"
    MigrationTools_folder = "MigrationTools"
    AntDataloader_folder = "AntDataloader"

    def __init__(self):
        if is_installed_package(self.dir_path):
            self.root_path = os.path.join(tempfile.gettempdir(), "salesforcexytools", "templates")
            packageFile = os.path.dirname(self.dir_path)
            extract_template(packageFile)
        else:
            self.root_path = self.dir_path

        self.template_migration_tools_path = os.path.join(self.root_path, self.template_folder, self.MigrationTools_folder)
        self.template_ant_dataloader_path = os.path.join(self.root_path, self.template_folder, self.AntDataloader_folder)

    def get_file(self, sub_folder, name):
        template_path = os.path.join(self.root_path, self.template_folder, sub_folder, name)
        with open(template_path) as fp:
            template = fp.read()
        return template

    def build_migration_tools(self, save_path, config_data):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self._copy_all(self.template_migration_tools_path, save_path)
        build_properties_src = self.get_file(self.MigrationTools_folder, "build.properties")
        build_properties_src = build_properties_src.format(**config_data)
        self._save_file(os.path.join(save_path, "build.properties"), build_properties_src)

        build_xml_src = self.get_file(self.template_migration_tools_path, "build.xml")
        build_xml_src = build_xml_src.replace("{jar_path}", config_data["jar_path"])
        self._save_file(os.path.join(save_path, "build.xml"), build_xml_src)
    
    def build_ant_dataloader(self, save_path, config_data):
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        self._copy_all(self.template_ant_dataloader_path, save_path)
        build_properties_src = self.get_file(self.template_ant_dataloader_path, "config.properties")
        build_properties_src = build_properties_src.format(**config_data)
        self._save_file(os.path.join(save_path, "config.properties"), build_properties_src)
        
        build_xml_src = self.get_file(self.template_ant_dataloader_path, "build.xml")
        build_xml_src = build_xml_src.replace("{dataloader_jar_path}", config_data["dataloader_jar_path"]).replace("{ant_export_xml}", config_data["ant_export_xml"])
        self._save_file(os.path.join(save_path, "build.xml"), build_xml_src)


    def _copy_all(self, org_path, dist_path):
        for file_name in os.listdir(org_path):
            full_file_name = os.path.join(org_path, file_name)
            if (os.path.isfile(full_file_name)):
                shutil.copy(full_file_name, dist_path)

    def _save_file(self, full_path, content, encoding='utf-8'):
        try:
            fp = open(full_path, "w", encoding=encoding)
            fp.write(content)
        except Exception as e:
            print('save file error! ' + full_path)
        finally:
            fp.close()

def is_installed_package(fileName):
    return ".sublime-package" in fileName

def extract_template(package_path):
    print("package_path" + package_path)
    root_path = os.path.join(tempfile.gettempdir(), "salesforcexytools")
    try:
        zfile = zipfile.ZipFile(package_path, 'r')
        for filename in zfile.namelist():
            if filename.endswith('/'): continue
            if filename.endswith('.py'): continue
            if filename.startswith("templates/"):
                f = os.path.join(root_path, filename)
                if not os.path.exists(os.path.dirname(f)):
                    os.makedirs(os.path.dirname(f))
                with open(f, "wb") as fp:
                    fp.write(zfile.read(filename))
    except zipfile.BadZipFile as ex:
        print(str(ex))
        return