#include <stdio.h>
#include <curl/curl.h>
#include <jansson.h>
#include <cstring>

// parliamentbomb sanity check file.
//
// this program sends a small heartbeat request to
// a main server to display server & client server status.
// this could be used to show server data at a web portal
// for example.
//
// this is all still a huge TODO, and will be completed later.
//
// depends on curl & jansson


// get env variables. currently supports
//
// HEARTBEAT_URL=<url or ip>
// > defines the place to send the heartbeat signal.

char* getEnvVar(const char* name) {
    FILE* file = fopen(".env", "r");
    if (file == NULL) {
        printf("Failed to open .env file\n");
        return NULL;
    }

    char line[256];
    while (fgets(line, sizeof(line), file)) {
        char varName[256];
        char varValue[256];
        sscanf(line, "%[^=]=%s", varName, varValue);
        if (strcmp(varName, name) == 0) {
            fclose(file);
            return strdup(varValue);
        }
    }

    fclose(file);
    return NULL;
}

size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    ((char*)userp)[0] = '\0';
    strncat(userp, contents, size*nmemb);
    return size*nmemb;
}

void sendHeartbeatRequest(const char *url) {
    CURL *curl;
    CURLcode res;
    char buffer[1024];

    curl_global_init(CURL_GLOBAL_DEFAULT);
    curl = curl_easy_init();
    if(curl) {
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, buffer);
        res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        } else {
            json_error_t error;
            json_t *root = json_loads(buffer, 0, &error);
            if(!root) {
                fprintf(stderr, "Error: %s\n", error.text);
            } else {
                json_t *status = json_object_get(root, "status");
                if(!status) {
                    fprintf(stderr, "No 'status' field in JSON response\n");
                } else {
                    printf("Status: %s\n", json_string_value(status));
                }
                json_decref(root);
            }
        }
        curl_easy_cleanup(curl);
    }
    curl_global_cleanup();
}

int main() {
    char *heartbeatUrl = getEnvVar("HEARTBEAT_URL");
    if (heartbeatUrl != NULL) {
        sendHeartbeatRequest(heartbeatUrl);
        free(heartbeatUrl);
    } else {
        printf("HEARTBEAT_URL not found in .env file\n");
    }

    return 0;
}
