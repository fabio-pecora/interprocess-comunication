#include <iostream>
#include <unistd.h>
#include <cstdlib>
#include <sys/wait.h>

using namespace std;

int main() {
    int N, fd1[2], fd2[2], fd3[2];
    pid_t pid;
    char buffer[100];

    // Get input from user
    cout << "Enter a value for N: ";
    cin >> N;

    // Create the pipes
    if (pipe(fd1) < 0 || pipe(fd2) < 0 || pipe(fd3) < 0) {
        cerr << "Failed to create pipes" << endl;
        return 1;
    }

    // Fork the process
    pid = fork();

    if (pid < 0) {
        cerr << "Failed to fork" << endl;
        return 1;
    }

    // Parent process
    if (pid > 0) {
        // Close unused pipe ends
        close(fd1[0]); // Parent write end of first pipe
        close(fd2[1]); // Parent read end of second pipe
        close(fd3[1]); // Parent read end of third pipe

        // Compute partial sum
        int sum = 0;
        for (int i = 1; i <= N/2; i++) {
            sum += i;
        }

        // Send partial sum to child
        write(fd1[1], &sum, sizeof(sum));

        // Wait for child to finish computing
        wait(NULL);

        // Receive partial sum from child
        int child_sum;
        read(fd2[0], &child_sum, sizeof(child_sum));

        // Compute final sum and print result
        int total_sum = sum + child_sum;
        cout << "The total sum of 1 to " << N << " is " << total_sum << endl;

        // Close pipe ends
        close(fd1[1]); // Parent write end of first pipe
        close(fd2[0]); // Parent read end of second pipe
        close(fd3[0]); // Parent write end of third pipe
    }

    // Child process
    else {
        // Close unused pipe ends
        close(fd1[1]); // Child read end of first pipe
        close(fd2[0]); // Child write end of second pipe
        close(fd3[0]); // Child read end of third pipe

        // Compute partial sum
        int sum = 0;
        for (int i = N/2 + 1; i <= N; i++) {
            sum += i;
        }

        // Receive message from parent
        read(fd1[0], buffer, sizeof(buffer));
        cout << "Child received message from parent: " << buffer << endl;

        // Send partial sum to parent
        write(fd2[1], &sum, sizeof(sum));

        // Send message to parent
        string message = "Child is done computing";
        write(fd3[1], message.c_str(), message.size() + 1);

        // Close pipe ends
        close(fd1[0]); // Child write end of first pipe
        close(fd2[1]); // Child read end of second pipe
        close(fd3[1]); // Child write end of third pipe
    }

    return 0;
}
