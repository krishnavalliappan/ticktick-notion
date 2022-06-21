from pprint import pprint

import secrets
from ticktick_admin import TicktickAdmin
from notion_admin import NotionAdmin


def matching_fn_using_Id(main_list, comparer_list, notion_main=False):
    """This function will compare main list with comparer list and return a list which does not have a match """
    if comparer_list:
        updated_list = []
        for main in main_list:
            match_found = False
            for comparer in comparer_list:
                try:
                    if notion_main:
                        condition = main["properties"]["Id_ticktick"]["rich_text"][0]["plain_text"] == comparer["id"]
                    else:
                        condition = comparer["properties"]["Id_ticktick"]["rich_text"][0]["plain_text"] == main["id"]
                    if condition:
                        match_found = True
                except:
                    pass
            if not match_found:
                updated_list.append(main)
        return updated_list
    else:
        return main_list


class TicktickNotion:
    def __init__(self):
        self.ticktick = None
        self.notion = None
        self.newly_added_task_ticktick = None
        self.newly_added_project_ticktick = None
        self.modified_task_ticktick = None
        self.modified_project_ticktick = None
        self.completed_tasks_ticktick = None
        self.archived_projects_ticktick = None
        self.deleted_projects_ticktick = None
        self.deleted_tasks_ticktick = None
        self.re_init()
        self.new_page_in_notion_if_project_added()
        self.new_page_in_notion_if_task_added()
        self.update_page_in_notion_if_project_modified()
        self.update_page_in_notion_if_task_modified()
        self.check_deleted_completed_tasks_ticktick()
        self.complete_page_in_notion_if_task_completed()
        self.deleted_page_in_notion_if_task_deleted()
        self.check_deleted_archived_project_ticktick()
        self.archive_page_in_notion_if_project_archived()

    def re_init(self):
        self.ticktick = TicktickAdmin(secrets.client_id, secrets.client_secret,
                                      secrets.uri, secrets.username, secrets.password)

        self.notion = NotionAdmin(secrets.secret_token,
                                  secrets.task_database_id,
                                  secrets.project_database_id)

    def modified_task_check(self):
        self.modified_task_ticktick = self.ticktick.modification_check_with_prevState()
        if self.modified_task_ticktick:
            return True
        else:
            return False

    def modified_project_check(self):
        self.modified_project_ticktick = self.ticktick.modification_check_with_prevState("projects")
        if self.modified_project_ticktick:
            return True
        else:
            return False

    def new_task_added_check(self):
        self.newly_added_task_ticktick = matching_fn_using_Id(self.ticktick.ticktick_tasks, self.notion.latest_tasks)
        if self.newly_added_task_ticktick:
            return True
        else:
            return False

    def new_project_added_check(self):
        self.newly_added_project_ticktick = matching_fn_using_Id(self.ticktick.ticktick_projects,
                                                                 self.notion.latest_projects)
        if self.newly_added_project_ticktick:
            return True
        else:
            return False

    def new_page_in_notion_if_task_added(self):
        if self.new_task_added_check():
            for task in self.newly_added_task_ticktick:
                self.notion.add_new_task_page(task=task)

    def new_page_in_notion_if_project_added(self):
        if self.new_project_added_check():
            for project in self.newly_added_project_ticktick:
                self.notion.add_new_project_page(project=project, client=self.ticktick.client)

    def update_page_in_notion_if_task_modified(self):
        if self.modified_task_check():
            for task in self.modified_task_ticktick:
                self.notion.update_page(dic=task)

    def update_page_in_notion_if_project_modified(self):
        if self.modified_project_check():
            for project in self.modified_project_ticktick:
                self.notion.update_page(dic=project, client=self.ticktick.client, update_type="project")

    def check_deleted_completed_tasks_ticktick(self):
        get_completed_deleted_tasks = self.ticktick.get_completed_deleted()
        self.completed_tasks_ticktick = get_completed_deleted_tasks["completed_list"]
        self.deleted_tasks_ticktick = get_completed_deleted_tasks["deleted_list"]

    def complete_page_in_notion_if_task_completed(self):
        if self.completed_tasks_ticktick:
            for task in self.completed_tasks_ticktick:
                self.notion.update_page(dic=task, complete=True)

    def deleted_page_in_notion_if_task_deleted(self):
        if self.deleted_tasks_ticktick:
            for task in self.deleted_tasks_ticktick:
                self.notion.update_page(dic=task, delete=True)

    def check_deleted_archived_project_ticktick(self):
        self.archived_projects_ticktick = self.ticktick.get_archived_deleted_projects()
        if self.archived_projects_ticktick:
            return True
        else:
            return False

    def archive_page_in_notion_if_project_archived(self):
        if self.archived_projects_ticktick:
            for project in self.archived_projects_ticktick:
                self.notion.update_page(dic=project, client=self.ticktick.client, update_type="project", complete=True)