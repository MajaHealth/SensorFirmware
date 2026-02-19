#ifndef JSON_TCP_SEVER_H
#define JSON_TCP_SEVER_H


#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <cstring>
#include <atomic>
#include <string>
#include <thread>
#include <chrono>
#include <poll.h>

class JSON_TCP_sever
{
public:
    JSON_TCP_sever(int port,
                   std::string* request_json_ptr,
                   std::atomic<bool>* request_ready_flag_ptr,
                   std::string* response_json_ptr,
                   std::atomic<bool>* response_ready_flag_ptr)
        : _port(port),
          _server_fd(-1),
          _request_json(request_json_ptr),
          _request_ready_flag(request_ready_flag_ptr),
          _response_json(response_json_ptr),
          _response_ready_flag(response_ready_flag_ptr),
          _server_running(false)
    {}

    ~JSON_TCP_sever()
    {
        Stop();
    }

    void Start()
    {
        if (_server_fd != -1)
        {
            std::cerr << "Server already running." << std::endl;
            return;
        }

        _server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (_server_fd == -1)
        {
            perror("socket creation failed");
            return;
        }


        int flags = fcntl(_server_fd, F_GETFL, 0);
        if (flags == -1)
        {
            perror("fcntl F_GETFL error (server)");
            close(_server_fd);
            _server_fd = -1;
            return;
        }
        if (fcntl(_server_fd, F_SETFL, flags | O_NONBLOCK) == -1)
        {
            perror("fcntl F_SETFL O_NONBLOCK error (server)");
            close(_server_fd);
            _server_fd = -1;
            return;
        }


        int optval = 1;
        if (setsockopt(_server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &optval, sizeof(optval)) < 0)
        {
            perror("setsockopt failed");
            close(_server_fd);
            _server_fd = -1;
            return;
        }

        sockaddr_in address;
        memset(&address, 0, sizeof(address));
        address.sin_family = AF_INET;
        address.sin_addr.s_addr = INADDR_ANY;
        address.sin_port = htons(_port);

        if (bind(_server_fd, (sockaddr*)&address, sizeof(address)) < 0)
        {
            perror("bind failed");
            close(_server_fd);
            _server_fd = -1;
            return;
        }

        if (listen(_server_fd, 3) < 0)
        {
            perror("listen failed");
            close(_server_fd);
            _server_fd = -1;
            return;
        }

        std::cout << "JSON Server started on port " << _port << std::endl;
        _server_running.store(true, std::memory_order_release);
        _server_thread = std::thread(&JSON_TCP_sever::server_loop, this);
    }


    void Stop()
    {
        if (_server_fd != -1)
        {
            _server_running.store(false, std::memory_order_release);
            shutdown(_server_fd, SHUT_RDWR);
            close(_server_fd);
            _server_fd = -1;
            if (_server_thread.joinable())
            {
                _server_thread.join();
            }
            std::cout << "Command Server stopped." << std::endl;
        }
    }



    bool is_socket_readable(int socket_fd)
    {
        if (socket_fd == -1)
        {
            return false;
        }

        struct pollfd pfd;
        pfd.fd = socket_fd;
        pfd.events = POLLIN;
        int ret = poll(&pfd, 1, 0);

        if (ret == -1)
        {
            return false;
        }

        if (ret > 0)
        {
            if (pfd.revents & POLLIN)
            {
                return true;
            }
        }
        return false;
    }


    bool is_client_connected(int socket_fd)
    {
        if (socket_fd == -1)
        {
            return false;
        }
        ssize_t zero_bytes_sent = send(socket_fd, "", 0, MSG_NOSIGNAL);
        if (zero_bytes_sent < 0)
        {
            if (errno != EAGAIN && errno != EWOULDBLOCK)
            {
                return false;
            }

            return true;
        }

        return true;
    }

    void server_loop()
    {
        std::cout <<"start server loop" << std::endl;
        sockaddr_in client_address;
        socklen_t addrlen = sizeof(client_address);
        char buffer[2048] = {0};

        while (_server_running.load(std::memory_order_acquire))
        {
            int client_socket = accept(_server_fd, (sockaddr*)&client_address, &addrlen);
            if (client_socket < 0)
            {
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
                continue;
            }

            int client_flags = fcntl(client_socket, F_GETFL, 0);
            if (client_flags == -1)
            {
                perror("fcntl F_GETFL error (client)");
                close(client_socket);
                continue;
            }
            if (fcntl(client_socket, F_SETFL, client_flags | O_NONBLOCK) == -1)
            {
                perror("fcntl F_SETFL O_NONBLOCK error (client)");
                close(client_socket);
                continue;
            }

            std::cout << "Connection accepted from " << inet_ntoa(client_address.sin_addr) << ":"
                      << ntohs(client_address.sin_port) << std::endl;

                      send(client_socket, "Connection accepted\n", 20, MSG_NOSIGNAL);

            ssize_t bytes_read;
            while (_server_running.load(std::memory_order_acquire))
            {
                if (is_client_connected(client_socket)==false)
                {
                    break;
                }

                if(is_socket_readable(client_socket)==true)
                {
                    bytes_read = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
                    if (bytes_read>0)
                    {
                        buffer[bytes_read] = '\0';
                        std::string received_json_command(buffer);
                        std::cout << "Server: Received command: '" << received_json_command << "'" << std::endl;

                        _response_ready_flag->store(false, std::memory_order_release);

                        if(_request_ready_flag->load(std::memory_order_acquire)==false)
                        {
                            *_request_json = received_json_command;
                            _request_ready_flag->store(true, std::memory_order_release);
                        }
                    }
                    else if (bytes_read == 0)
                    {
                        break;
                    }
                    else if (bytes_read < 0)
                    {
                        if (errno == EAGAIN || errno == EWOULDBLOCK)
                        {

                        }
                        else
                        {
                            perror("recv error");
                            break;
                        }
                    }
                }


                if(_response_ready_flag->load(std::memory_order_acquire))
                {
                    std::string response_to_send = *_response_json;
                    _response_ready_flag->store(false, std::memory_order_release);

                    std::cout << "Sending to client: '" << response_to_send << "'" << std::endl;
                    send(client_socket, response_to_send.c_str(), response_to_send.length(), MSG_NOSIGNAL);
                    send(client_socket, "\n", 1, MSG_NOSIGNAL);
                }

                std::this_thread::yield();
                std::this_thread::sleep_for(std::chrono::milliseconds(100));
            }
            close(client_socket);
            std::cout << "Client disconnected." << std::endl;
        }
    }

protected:

private:


    int _port;
    std::thread _server_thread;
    int _server_fd; // File descriptor для сокета сервера

    // Вказівники на спільні ресурси
    std::string* _request_json;
    std::atomic<bool>* _request_ready_flag;
    std::string* _response_json;
    std::atomic<bool>* _response_ready_flag;

    std::atomic<bool> _server_running;
};

#endif // JSON_TCP_SEVER_H



