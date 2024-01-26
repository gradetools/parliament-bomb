#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/prctl.h>
#include <signal.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>

// parliamentbomb bootstrapper & control panel
// use make to build, and ./parliamentctl to run

void startSystemdServices() {
    // placeholder for future parliamentctl interfaces with systemd.
    // to be added
    printf("\033[1mParliamentbomb Bootstrapper\033[0m\n");
    printf("Launching Parliamentbomb..\n");
    printf("Starting systemd Services: N/A\n");
}

void runPythonScript(const char *outputFile) {

    int pipefd[2];
    pid_t pid;

    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    pid = fork();

    if (pid == -1) {
        perror("fork");
        exit(EXIT_FAILURE);
    }

    if (pid == 0) { // Child process
        close(pipefd[0]); 

        // hiding output from appearing in terminal
        dup2(pipefd[1], STDOUT_FILENO);
        dup2(pipefd[1], STDERR_FILENO);
        close(pipefd[1]);

        // run initbridge.py
        prctl(PR_SET_PDEATHSIG, SIGHUP); 
        execlp("python", "python", "initBridge.py", NULL);

        // If execlp fails
        perror("execlp");
        exit(EXIT_FAILURE);
    } else { // Parent process
        close(pipefd[1]);

        printf("Launching Parliamentbomb to Discord bridge script...\n");
        printf("\033[1;32mDone! Use 'tail -f' to look at live logs.\033[0m\n");
        printf("Log Location: <logfile>\n");


        FILE *outputFilePtr = fopen(outputFile, "w");
        if (outputFilePtr == NULL) {
            perror("fopen");
            exit(EXIT_FAILURE);
        }

        char buffer[1024];
        ssize_t bytesRead;
        while ((bytesRead = read(pipefd[0], buffer, sizeof(buffer))) > 0) {
            fwrite(buffer, 1, bytesRead, outputFilePtr);
        }

        fclose(outputFilePtr);

        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status)) {
            printf("Python script exited with status %d\n", WEXITSTATUS(status));
        } else {
            printf("Python script exited abnormally\n");
        }

        close(pipefd[0]);
    }
}

pid_t findPythonScriptPID() {
    pid_t pythonScriptPID = -1;
    FILE *cmdlineFile = popen("pgrep -o -f 'python initBridge.py'", "r");
    if (cmdlineFile != NULL) {
        fscanf(cmdlineFile, "%d", &pythonScriptPID);
        fclose(cmdlineFile);
    }
    return pythonScriptPID;
}


void handleKillOption() { 
    // under construction doesn't seem to be working
    if (system("pkill -SIGINT -f 'python main.py'") == 0) {
        printf("Sent SIGINT to all instances of the Python script.\n");
    } else {
        perror("system");
    }
}

int main(int argc, char *argv[]) {
    if (argc == 2 && strcmp(argv[1], "--kill") == 0) {
        handleKillOption();
        return EXIT_SUCCESS;
    }

    if (argc == 1) {
        printf("\033[1mparliamentctl\033[0m\n");
        printf("USAGE: parliamenctl [OPTION]\n");
        printf("parliamentbomb control tool\n\n");
        printf("%s --init             launch parliamentbomb\n", argv[0]);
        printf("%s --kill             kill parliamentbomb\n", argv[0]); 
        printf("%s --force-sync       force sync to other servers <coming soon>\n\n", argv[0]);
        printf("run 'man -l parliamentctl.1' to read extra documentation"); 
        exit(EXIT_SUCCESS);
    }

    if (argc != 2 || (strcmp(argv[1], "--init") != 0 && strcmp(argv[1], "--kill") != 0)) {
        printf("Invalid arguments. See the help card below:\n");
        printf("parliamentbomb control tool\n\n");
        printf("%s --init             launch parliamentbomb\n", argv[0]);
        printf("%s --kill             kill parliamentbomb\n", argv[0]); 
        printf("%s --force-sync       force sync to other servers <coming soon>\n\n", argv[0]);
        printf("run 'man -l parliamentctl.1' to read extra documentation"); 
        return EXIT_FAILURE;
    }

    if (strcmp(argv[1], "--init") == 0) {
        startSystemdServices();

        const char *homeDir = getenv("HOME");
        if (homeDir == NULL) {
            fprintf(stderr, "Error: HOME environment variable not set.\n");
            return EXIT_FAILURE;
        }

        // build log files  
        time_t t = time(NULL);
        struct tm *tm_info = localtime(&t);
        char timestamp[20];
        strftime(timestamp, sizeof(timestamp), "%Y-%m-%d_%H-%M-%S", tm_info);

        char logDir[100];
        snprintf(logDir, sizeof(logDir), "%s/.parliamentbomber/logfiles", homeDir);

        // check if the log directory exists
        struct stat st = {0};
        if (stat(logDir, &st) == -1) {
            // If the directory doesn't exist, create it
            if (mkdir(logDir, 0700) == -1) {
                perror("mkdir");
                return EXIT_FAILURE;
            }
        }

        char outputFile[100];
        snprintf(outputFile, sizeof(outputFile), "%s/log_%s.txt", logDir, timestamp);

        // redirect data to logfile 
        runPythonScript(outputFile);
    }

    return EXIT_SUCCESS;
}
