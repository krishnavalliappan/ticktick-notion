import json
import notion_helpers

import requests


class NotionAdmin:
    def __init__(self, token, task_db_id, project_db_id):
        self.headers = {
            'Authorization': "Bearer " + token,
            'Content-Type': 'application/json',
            'Notion-Version': '2022-02-22'
        }
        self.base_db_url = "https://api.notion.com/v1/databases/"
        self.page_url = 'https://api.notion.com/v1/pages'
        self.project_db_id = project_db_id
        self.task_db_id = task_db_id
        self.latest_tasks = self.query_db(self.task_db_id)["results"]
        self.latest_projects = self.query_db(self.project_db_id)["results"]

    def query_db(self, db_id, field_name=None, field_value=None):
        data = None  # initializing data with none
        if field_value and field_name:
            filter_ = {
                "filter": {
                    "property": field_name,
                    "rich_text": {
                        "contains": field_value
                    }
                }
            }
            data = json.dumps(filter_)
        response_data = requests.post(f"{self.base_db_url}{db_id}/query", headers=self.headers, data=data)
        return response_data.json()

    def add_new_task_page(self, task):
        response = requests.post(self.page_url, headers=self.headers,
                                 data=self.page_prop_builder(task=task))
        print(response.json())

    def add_new_project_page(self, project, client):
        response = requests.post(self.page_url, headers=self.headers,
                                 data=self.project_prop_builder(project=project, client=client))
        print(response.json())

    def page_prop_builder(self, task, update=False, complete=False, delete=False):
        newPageData = {
            "parent": {"database_id": self.task_db_id},
            "properties": {
                "Title": {
                    "title": [
                        {
                            "text": {
                                "content": task["title"]
                            }
                        }
                    ]
                },
                "Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task["desc"]
                            }
                        }
                    ]
                },
                "Start Date": {
                    "date": {
                        "start": str(notion_helpers.ticktickDate_to_isoFormat(task["startDate"],
                                                                              task[
                                                                                  "timeZone"])) if "startDate" in task.keys() else None
                    }
                },
                "End Date": {
                    "date": {
                        "start": str(notion_helpers.ticktickDate_to_isoFormat(task["dueDate"],
                                                                              task[
                                                                                  "timeZone"])) if "dueDate" in task.keys() else None
                    }
                },
                "Id_ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task["id"]
                            }
                        }
                    ]
                },
                "ProjectId_ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": task["projectId"]
                            }
                        }
                    ]
                },
                "Priority": {
                    "select": {
                        "name": notion_helpers.priority_convert(task["priority"])
                    }
                },
                "Progress_ticktick": {
                    "number": task["progress"]
                },
                "ModifiedTime_ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(notion_helpers.ticktickDate_to_isoFormat(task["modifiedTime"],
                                                                                        task["timeZone"]))
                            }
                        }
                    ]
                },
                "CreatedTime_ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": str(notion_helpers.ticktickDate_to_isoFormat(task["createdTime"],
                                                                                        task["timeZone"]))
                            }
                        }
                    ]
                },
                "Pomo Count": {
                    "number": notion_helpers.focus_summary_convert(task["focusSummaries"], "pomo")
                },
                "Focus Time in Min.": {
                    "number": notion_helpers.focus_summary_convert(task["focusSummaries"], "focus_time")
                },
                "Project": {
                    "relation": [
                        {
                            "id": self.query_db(db_id=self.project_db_id, field_value=task["projectId"],
                                                field_name="Id_ticktick")["results"][0]["id"]
                        }
                    ]
                },
                "Kind": {
                    "select": {
                        "name": notion_helpers.kind_converter(task["kind"])
                    }
                },
                "Recurring Task": {
                    "checkbox": False if not notion_helpers.recurring_task_check(task=task) else True
                },
                "Completed": {
                    "checkbox": complete if complete else False
                }
            },
            "archived": delete,
        }
        if task["items"] or task["content"]:
            newPageData["children"] = notion_helpers.add_checklist_content(task)
        if "startDate" not in task.keys():
            newPageData["properties"].pop("Start Date")
        if "dueDate" not in task.keys():
            newPageData["properties"].pop("End Date")
        if "startDate" in task.keys():
            if task["startDate"] == task["dueDate"]:
                newPageData["properties"].pop("End Date")
        if update:
            newPageData.pop("parent")
            if "children" in newPageData.keys():
                newPageData.pop("children")
        data = json.dumps(newPageData)

        return data

    def project_prop_builder(self, project, client, update=False, complete=False):
        new_project_data = {
            "parent": {"database_id": self.project_db_id},
            "properties": {
                "Project Name": {
                    "title": [
                        {
                            "text": {
                                "content": project["name"] if project["name"].replace(" ", "").isalnum() else "".join(
                                    [string for string in project["name"].replace(" ", "*") if
                                     string.isalnum() or string in ["*", "&", "'", "-"]]).replace("*", " ")
                            }
                        }
                    ]
                },
                "Id_ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": project["id"]
                            }
                        }
                    ]
                },
                "ModifiedTime_Ticktick": {
                    "rich_text": [
                        {
                            "text": {
                                "content": project["modifiedTime"]
                            }
                        }
                    ]
                },
                "Area": {
                    "select": {
                        "name": client.get_by_id(project["groupId"], search='project_folders')["name"] if project[
                                                                                                              "groupId"] != "NONE" else "No Area"
                    }
                },
                "Archive": {
                    "checkbox": complete if complete else False
                }
            }
        }

        if update:
            new_project_data.pop("parent")

        if not project["name"].replace(" ", "").isalnum():
            new_project_data["icon"] = {
                "emoji": project["name"][0]
            }

        data = json.dumps(new_project_data)

        return data

    def update_page(self, dic, update_type="task", complete=False, client=None, delete=False):
        #     find the page_id of the task in notion
        if update_type == "task":
            db_id = self.task_db_id
            builder_data = self.page_prop_builder(task=dic["tasks"], update=True, complete=complete, delete=delete)
        else:
            db_id = self.project_db_id
            builder_data = self.project_prop_builder(project=dic["projects"], client=client,  update=True, complete=complete)

        update_notion_page_id = self.query_db(db_id=db_id, field_value=dic["id"],
                                              field_name="Id_ticktick")["results"][0]["id"]
        update_url = f"https://api.notion.com/v1/pages/{update_notion_page_id}"
        response = requests.request("PATCH", update_url, headers=self.headers,
                                    data=builder_data)
        print(response.json())
