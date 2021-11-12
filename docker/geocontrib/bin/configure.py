#!/usr/bin/env python3
import os

from jinja2 import Environment, FileSystemLoader
import yaml


def build_configuration_file(template_dir, template, data, destination):
    j2_env = Environment(loader=FileSystemLoader(template_dir),
                         trim_blocks=True,
                         keep_trailing_newline=True)

    result = j2_env.get_template(template).render(**data)

    with open(destination, "wb") as destination:
        destination.write(result.encode("utf-8"))


def main():
    with open("configure.yaml") as conf_stream:
        config = yaml.load(conf_stream, Loader=yaml.BaseLoader)
    data = dict()
    variables = config.get("variables", [])
    envs = config.get("environments", ["qualif", "preprod", "prod"])
    for deploy in envs:
        print("Environment %s" % deploy)

        if not os.path.exists(deploy):
            os.mkdir(deploy)

        for var in variables:
            env_var = variables[var].get('env_' + deploy)
            if env_var:
                data[var] = os.environ.get(env_var)
                print(" Parameter Environ %s: %s" % (var, data[var]))
            else:
                data[var] = variables[var].get(deploy)

                print(" Parameter %s: %s" % (var, data[var]))

        for template in config.get('files'):
            output_file = os.path.join(deploy, template["destination"])
            build_configuration_file("templates",
                                     template["template"],
                                     data,
                                     output_file)
            print(" File : %s" % output_file)


if __name__ == "__main__":
    main()
