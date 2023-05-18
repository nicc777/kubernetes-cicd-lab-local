# Context

Various webhook traffic dumps for merge requests

# Final Merge

This is the HTTP request dump (source: Wireshark) when a merge request is finally merged in Gitlab, with a webhook configured to Jenkins.

## Request

### Headers

```text
POST /project/awesome-application-ci HTTP/1.1
Content-Type: application/json
User-Agent: GitLab/15.9.8
X-Gitlab-Event: Merge Request Hook
X-Gitlab-Instance: http://gitlab.example.tld
X-Gitlab-Token: 8dfc9f603b7cd193a142ec33b8aa5a0a
X-Gitlab-Event-Uuid: 09eaeca9-6280-4f32-95bf-577daa4b5c0e
Accept-Encoding: gzip;q=1.0,deflate;q=0.6,identity;q=0.3
Accept: */*
Connection: close
Host: jenkins.example.tld:8081
Content-Length: 3977
```

### Body

```json
{
    "object_kind": "merge_request",
    "event_type": "merge_request",
    "user": {
        "id": 1,
        "name": "Administrator",
        "username": "root",
        "avatar_url": "https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=80&d=identicon",
        "email": "[REDACTED]"
    },
    "project": {
        "id": 3,
        "name": "application-repo-01",
        "description": null,
        "web_url": "http://gitlab.example.tld/lab/application-repo-01",
        "avatar_url": null,
        "git_ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
        "git_http_url": "http://gitlab.example.tld/lab/application-repo-01.git",
        "namespace": "lab",
        "visibility_level": 0,
        "path_with_namespace": "lab/application-repo-01",
        "default_branch": "main",
        "ci_config_path": null,
        "homepage": "http://gitlab.example.tld/lab/application-repo-01",
        "url": "git@gitlab.example.tld:lab/application-repo-01.git",
        "ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
        "http_url": "http://gitlab.example.tld/lab/application-repo-01.git"
    },
    "object_attributes": {
        "assignee_id": null,
        "author_id": 1,
        "created_at": "2023-05-18 04:39:56 UTC",
        "description": "",
        "head_pipeline_id": 3,
        "id": 2,
        "iid": 2,
        "last_edited_at": null,
        "last_edited_by_id": null,
        "merge_commit_sha": "571028f2925c0c210e61dfdc0acc8918a5ab7a1a",
        "merge_error": null,
        "merge_params": {
            "force_remove_source_branch": "1"
        },
        "merge_status": "can_be_merged",
        "merge_user_id": null,
        "merge_when_pipeline_succeeds": false,
        "milestone_id": null,
        "source_branch": "issue-1",
        "source_project_id": 3,
        "state_id": 3,
        "target_branch": "main",
        "target_project_id": 3,
        "time_estimate": 0,
        "title": "#1 - Updated version",
        "updated_at": "2023-05-18 04:46:48 UTC",
        "updated_by_id": null,
        "url": "http://gitlab.example.tld/lab/application-repo-01/-/merge_requests/2",
        "source": {
            "id": 3,
            "name": "application-repo-01",
            "description": null,
            "web_url": "http://gitlab.example.tld/lab/application-repo-01",
            "avatar_url": null,
            "git_ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "git_http_url": "http://gitlab.example.tld/lab/application-repo-01.git",
            "namespace": "lab",
            "visibility_level": 0,
            "path_with_namespace": "lab/application-repo-01",
            "default_branch": "main",
            "ci_config_path": null,
            "homepage": "http://gitlab.example.tld/lab/application-repo-01",
            "url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "http_url": "http://gitlab.example.tld/lab/application-repo-01.git"
        },
        "target": {
            "id": 3,
            "name": "application-repo-01",
            "description": null,
            "web_url": "http://gitlab.example.tld/lab/application-repo-01",
            "avatar_url": null,
            "git_ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "git_http_url": "http://gitlab.example.tld/lab/application-repo-01.git",
            "namespace": "lab",
            "visibility_level": 0,
            "path_with_namespace": "lab/application-repo-01",
            "default_branch": "main",
            "ci_config_path": null,
            "homepage": "http://gitlab.example.tld/lab/application-repo-01",
            "url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "ssh_url": "git@gitlab.example.tld:lab/application-repo-01.git",
            "http_url": "http://gitlab.example.tld/lab/application-repo-01.git"
        },
        "last_commit": {
            "id": "6f51ab56bd45324314cf7ee143cde7964cdbcb9f",
            "message": "#1 - Updated version\n",
            "title": "#1 - Updated version",
            "timestamp": "2023-05-16T05:16:25+02:00",
            "url": "http://gitlab.example.tld/lab/application-repo-01/-/commit/6f51ab56bd45324314cf7ee143cde7964cdbcb9f",
            "author": {
                "name": "Nico Coetzee",
                "email": "nico.coetzee@capgemini.com"
            }
        },
        "work_in_progress": false,
        "total_time_spent": 0,
        "time_change": 0,
        "human_total_time_spent": null,
        "human_time_change": null,
        "human_time_estimate": null,
        "assignee_ids": [],
        "reviewer_ids": [],
        "labels": [],
        "state": "merged",
        "blocking_discussions_resolved": true,
        "first_contribution": false,
        "detailed_merge_status": "not_open",
        "action": "merge"
    },
    "labels": [],
    "changes": {
        "state_id": {
            "previous": 4,
            "current": 3
        },
        "updated_at": {
            "previous": "2023-05-18 04:46:48 UTC",
            "current": "2023-05-18 04:46:48 UTC"
        }
    },
    "repository": {
        "name": "application-repo-01",
        "url": "git@gitlab.example.tld:lab/application-repo-01.git",
        "description": null,
        "homepage": "http://gitlab.example.tld/lab/application-repo-01"
    }
}
```

## Response

```text
HTTP/1.1 200 OK
Date: Thu, 18 May 2023 04:46:48 GMT
Connection: close
X-Content-Type-Options: nosniff
Server: Jetty(10.0.13)
```