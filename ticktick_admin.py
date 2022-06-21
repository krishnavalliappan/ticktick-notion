import pickle
from datetime import datetime, timedelta
from pprint import pprint

from ticktick.oauth2 import OAuth2  # OAuth2 Manager
from ticktick.api import TickTickClient  # Main Interface


class TicktickAdmin:
    def __init__(self, client_id, client_secret, redirect_uri, username, password):
        self.auth_client = OAuth2(client_id=client_id,
                                  client_secret=client_secret,
                                  redirect_uri=redirect_uri)
        self.username = username
        self.password = password
        self.client = None
        self.authenticate()
        self.prev_state = None
        self.load_prev_state()
        self.new_state = self.reading_state()
        self.saving_state()
        self.ticktick_tasks = self.new_state["tasks"]
        self.ticktick_projects = self.new_state["projects"]

    def authenticate(self):
        self.client = TickTickClient(self.username, self.password, self.auth_client)

    def reading_state(self):
        state = self.client.state
        projects = []
        for project in state["projects"]:
            if not project["closed"]:
                projects.append(project)
        state.pop("projects")
        state["projects"] = projects
        return state

    def saving_state(self):
        if self.new_state:
            with open('prev_state.pkl', 'wb') as f:
                pickle.dump(self.new_state, f)

    def load_prev_state(self):
        try:
            with open("prev_state.pkl", "rb") as f:
                self.prev_state = pickle.load(f)
        except:
            self.prev_state = self.reading_state()

    def modification_check_with_prevState(self, check_type="tasks"):
        modi_dic_list = []
        for i in range(len(self.new_state[check_type])):
            for j in range(len(self.prev_state[check_type])):
                if self.new_state[check_type][i]["id"] == self.prev_state[check_type][j]["id"]:
                    if self.new_state[check_type][i] != self.prev_state[check_type][j]:
                        properties = []
                        for keys in self.new_state[check_type][i].keys():
                            if self.new_state[check_type][i][keys] != self.prev_state[check_type][j][keys]:
                                properties.append(keys)
                        modi_dic_list.append({
                            "id": self.new_state[check_type][i]["id"],
                            check_type: self.new_state[check_type][i],
                        })
        return modi_dic_list

    def tasks_proj_missing_prev_state(self, check_type="tasks"):
        missing_list = []
        for i in range(len(self.prev_state[check_type])):
            match_found = False
            for j in range(len(self.new_state[check_type])):
                if self.prev_state[check_type][i]["id"] == self.new_state[check_type][j]["id"]:
                    match_found = True
            if not match_found:
                missing_list.append({
                    "id": self.prev_state[check_type][i]["id"],
                    check_type: self.prev_state[check_type][i],
                })
        return missing_list

    def get_completed_deleted(self):
        missing_list = self.tasks_proj_missing_prev_state("tasks")
        completed_list = []
        deleted_list = []
        if missing_list:
            for task in missing_list:
                match_found = False
                for comp_task in self.client.task.get_completed(datetime.today() - timedelta(days=1), datetime.today()):
                    if task["id"] == comp_task["id"]:
                        match_found = True
                        completed_list.append({
                            "id": task["id"],
                            "tasks": task["tasks"],
                        })
                if not match_found:
                    deleted_list.append({
                        "id": task["id"],
                        "tasks": task["tasks"],
                    })

        return {
            "completed_list": completed_list,
            "deleted_list": deleted_list
        }

    def get_archived_deleted_projects(self):
        missing_list = self.tasks_proj_missing_prev_state("projects")
        archived_list = []
        for project in missing_list:
            match_found = False
            for project_all in self.client.state["projects"]:
                if project["id"] == project_all["id"]:
                    match_found = True
            if not match_found:
                archived_list.append(project)

        return archived_list
