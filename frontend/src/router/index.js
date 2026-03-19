import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const Home = () => import("../views/Home.vue");

const Templates = () => import("../views/Templates.vue");
const TemplatesShow = () => import("../components/templates/TemplatesDetails.vue");
const TemplatesForm = () => import("../components/templates/TemplatesForm.vue");
const TemplatesList = () => import("../components/templates/TemplatesList.vue");

const Applications = () => import("../views/Applications.vue");
const AppContent = () =>
  import("../components/applications/ApplicationDetailsComponents/AppContent.vue");
const AppProcesses = () =>
  import("../components/applications/ApplicationDetailsComponents/AppProcesses.vue");
const AppLogs = () =>
  import("../components/applications/ApplicationDetailsComponents/AppLogs.vue");
const AppStats = () =>
  import("../components/applications/ApplicationDetailsComponents/AppStats.vue");
const ApplicationDetails = () =>
  import("../components/applications/ApplicationDetails.vue");
const ApplicationsList = () =>
  import("../components/applications/ApplicationsList.vue");
const ApplicationsForm = () =>
  import("../components/applications/ApplicationsForm.vue");
const ApplicationDeployFromTemplate = () =>
  import("../components/applications/ApplicationDeployFromTemplate.vue");

const Project = () => import("../views/Project.vue");
const ProjectList = () => import("../components/compose/ProjectList.vue");
const ProjectDetails = () => import("../components/compose/ProjectDetails.vue");
const ProjectEditor = () => import("../components/compose/ProjectEditor.vue");

const Resources = () => import("../views/Resources.vue");
const ImageList = () => import("../components/resources/images/ImageList.vue");
const ImageDetails = () =>
  import("../components/resources/images/ImageDetails.vue");
const VolumeList = () =>
  import("../components/resources/volumes/VolumeList.vue");
const VolumeDetails = () =>
  import("../components/resources/volumes/VolumeDetails.vue");
const NetworkList = () =>
  import("../components/resources/networks/NetworkList.vue");
const NetworkDetails = () =>
  import("../components/resources/networks/NetworkDetails.vue");
const NetworkForm = () =>
  import("../components/resources/networks/NetworkForm.vue");

const UserSettings = () => import("../views/UserSettings.vue");
const ChangePasswordForm = () =>
  import("../components/userSettings/ChangePasswordForm.vue");
const UserInfo = () => import("../components/userSettings/UserInfo.vue");

const ServerSettings = () => import("../views/ServerSettings.vue");
const ServerInfo = () => import("../components/serverSettings/ServerInfo.vue");
const ServerVariables = () =>
  import("../components/serverSettings/ServerVariables.vue");
const Prune = () => import("../components/serverSettings/Prune.vue");
const ServerUpdate = () =>
  import("../components/serverSettings/ServerUpdate.vue");
const Theme = () => import("../components/serverSettings/Theme.vue");

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home
  },
  {
    path: "/templates",
    component: Templates,
    children: [
      {
        path: "",
        name: "View Templates",
        component: TemplatesList
      },
      {
        path: "new",
        name: "New Template",
        component: TemplatesForm
      },
      {
        path: ":templateId",
        name: "Template Details",
        component: TemplatesShow
      }
    ]
  },
  {
    path: "/apps",
    component: Applications,
    children: [
      {
        name: "Deploy",
        path: "deploy/:appId",
        component: ApplicationsForm
      },
      {
        name: "Edit",
        path: "edit/:appName",
        component: ApplicationsForm
      },
      {
        name: "Deploy from Template",
        path: "templates",
        component: ApplicationDeployFromTemplate
      },
      {
        name: "View Applications",
        path: "/",
        component: ApplicationsList
      },
      {
        name: "Add Application",
        path: "deploy",
        component: ApplicationsForm
      },
      {
        path: ":appName",
        component: ApplicationDetails,
        children: [
          {
            name: "Processes",
            path: "top",
            component: AppProcesses
          },
          {
            name: "Info",
            path: "info",
            component: AppContent
          },
          {
            name: "Logs",
            path: "logs",
            component: AppLogs
          },
          {
            name: "Stats",
            path: "stats",
            component: AppStats
          }
        ]
      }
    ]
  },
  {
    path: "/projects",
    component: Project,
    children: [
      {
        name: "View Projects",
        path: "/",
        component: ProjectList
      },
      {
        name: "Edit Project",
        path: ":projectName/edit",
        component: ProjectEditor
      },
      {
        name: "Project Details",
        path: ":projectName",
        component: ProjectDetails
      }
    ]
  },
  {
    path: "/user",
    component: UserSettings,
    children: [
      {
        name: "User Info",
        path: "info",
        component: UserInfo
      },
      {
        name: "Change Password",
        path: "changePassword",
        component: ChangePasswordForm
      }
    ]
  },
  {
    path: "/settings",
    component: ServerSettings,
    children: [
      {
        name: "Server Info",
        path: "info",
        component: ServerInfo
      },
      {
        name: "Theme",
        path: "theme",
        component: Theme
      },
      {
        name: "Template Variables",
        path: "templateVariables",
        component: ServerVariables
      },
      {
        name: "Prune",
        path: "prune",
        component: Prune
      },
      {
        name: "Update Yacht",
        path: "update",
        component: ServerUpdate
      }
    ]
  },
  {
    path: "/resources",
    component: Resources,
    children: [
      {
        name: "Images",
        path: "images",
        component: ImageList
      },
      {
        path: "images/:imageid",
        name: "Image Details",
        component: ImageDetails
      },
      {
        name: "Volumes",
        path: "volumes",
        component: VolumeList
      },
      {
        path: "volumes/:volumeName",
        name: "Volume Details",
        component: VolumeDetails
      },
      {
        name: "Networks",
        path: "networks",
        component: NetworkList
      },
      {
        path: "networks/new",
        name: "New Network",
        component: NetworkForm
      },
      {
        path: "networks/:networkid",
        name: "Network Details",
        component: NetworkDetails
      }
    ]
  }
];

const router = new VueRouter({
  mode: "hash",
  base: "",
  routes
});

export default router;
