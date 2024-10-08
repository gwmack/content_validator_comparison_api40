import looker_sdk
#from looker_sdk import models
# from looker_sdk.rtl import transport
import argparse
import configparser
import hashlib
import csv

config_file = "looker.ini"
sdk = looker_sdk.init40("looker.ini")


def main():
    """Compare two distinct content validator runs."""
    parser = argparse.ArgumentParser(
        description='Compare two distinct content validator runs.'
    )
    parser.add_argument(
        '--sudo_user_id', 
        '-s',
        type=str,
        required=False, 
        help='Optionally supply a user_id to sudo as')
    parser.add_argument(
        '--dev', 
        '-d',
        required=False,
        action="store_true" ,
        help='Run the script in dev mode')
    args = parser.parse_args()
    if args.sudo_user_id:
        sdk.login_user(args.sudo_user_id)
    if args.dev:
        checkout_dev_branch()
    base_url = get_base_url()
    space_data = get_space_data()
    print("Checking for broken content for the first time.")
    broken_content_one = parse_broken_content(
        base_url, get_broken_content(), space_data
    )
    input("""
    Do what you need to do in Looker. 
    Press enter/return when you're ready to validate again.
    """)
    print("Checking broken content for the second time.")
    broken_content_two = parse_broken_content(
        base_url, get_broken_content(), space_data
    )
    new_broken_content = compare_broken_content(broken_content_one, broken_content_two)
    if new_broken_content:
        write_broken_content_to_file(new_broken_content, "new_broken_content.csv")
    else:
        print("No new broken content.")


def get_base_url():
    """ Pull base url from looker.ini, remove port"""
    config = configparser.ConfigParser()
    config.read(config_file)
    full_base_url = config.get("Looker", "base_url")
    base_url = sdk.auth.settings.base_url[: full_base_url.index(":19999")]
    return base_url


def get_space_data():
    """Collect all space information"""
    space_data = sdk.all_spaces(fields="id, parent_id, name")
    return space_data


def get_broken_content():
    """Collect broken content"""
    broken_content = sdk.content_validation().content_with_errors
    return broken_content


def parse_broken_content(base_url, broken_content, space_data):
    """Parse and return relevant data from content validator"""
    output = []
    for item in broken_content:
        if item.dashboard:
            content_type = "dashboard"
        else:
            content_type = "look"
        item_content_type = getattr(item, content_type)
        if item_content_type is not None:
            id = item_content_type.id
            name = item_content_type.title
            space_id = item_content_type.space.id
            space_name = item_content_type.space.name
            errors = item.errors
            url = f"{base_url}/{content_type}s/{id}"
            space_url = "{}/spaces/{}".format(base_url, space_id)
            if content_type == "look":
                element = None
            else:
                dashboard_element = item.dashboard_element
                element = dashboard_element.title if dashboard_element else None
            # Lookup additional space information
            space = next(i for i in space_data if str(i.id) == str(space_id))
            parent_space_id = space.parent_id
            # Old version of API  has issue with None type for all_space() call
            if parent_space_id is None or parent_space_id == "None":
                parent_space_url = None
                parent_space_name = None
            else:
                parent_space_url = "{}/spaces/{}".format(base_url, parent_space_id)
                parent_space = next(
                    (i for i in space_data if str(i.id) == str(parent_space_id)), None
                )
                # Handling an edge case where space has no name. This can happen
                # when users are improperly generated with the API
                try:
                    parent_space_name = parent_space.name
                except AttributeError:
                    parent_space_name = None
            # Create a unique hash for each record. This is used to compare
            # results across content validator runs
            unique_id = hashlib.md5(
                "-".join(
                    [str(id), str(element), str(name), str(errors), str(space_id)]
                ).encode()
            ).hexdigest()
            data = {
                "unique_id": unique_id,
                "content_type": content_type,
                "name": name,
                "url": url,
                "dashboard_element": element,
                "space_name": space_name,
                "space_url": space_url,
                "parent_space_name": parent_space_name,
                "parent_space_url": parent_space_url,
                "errors": str(errors),
            }
            output.append(data)
        else:
            pass
    return output


def compare_broken_content(broken_content_prod, broken_content_dev):
    """Compare output between 2 content_validation runs"""
    unique_ids_prod = set([i["unique_id"] for i in broken_content_prod])
    unique_ids_dev = set([i["unique_id"] for i in broken_content_dev])
    new_broken_content_ids = unique_ids_dev.difference(unique_ids_prod)
    new_broken_content = []
    for item in broken_content_dev:
        if item["unique_id"] in new_broken_content_ids:
            new_broken_content.append(item)
    return new_broken_content


def checkout_dev_branch():
    """Enter dev workspace"""
    sdk.update_session(models.WriteApiSession(workspace_id="dev"))


def write_broken_content_to_file(broken_content, output_csv_name):
    """Export new content errors in dev branch to csv file"""
    try:
        with open(output_csv_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(broken_content[0].keys()))
            writer.writeheader()
            for data in broken_content:
                writer.writerow(data)
        print("Broken content information outputed to {}".format(output_csv_name))
    except IOError:
        print("I/O error")


main()
