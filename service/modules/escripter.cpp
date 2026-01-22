#include <pybind11/pybind11.h>
#include <fstream>
#include <string>
#include "modules/cppmodules/json.hpp"
#include <variant>
#include <cerrno>
#include <optional>

namespace py = pybind11;
using json = nlohmann::json;
class scripter
{
private:

    struct Pconfig
    {
        
    };
    struct ApiConfig {
        std::optional<std::string> id;
        std::optional<std::string> worker_id;
    };

    struct HttpConfig {
        bool enabled;
        std::string host;
        int port;
        std::optional<std::string> access_token;
        bool restricted;
    };
    
    struct ApiConfig {
        std::optional<std::string> id;
        std::optional<std::string> worker_id;
    };

    struct RandomXConfig {
        int init;
        int init_avx2;
        std::string mode;
        bool pages_1gb;
        bool rdmsr;
        bool wrmsr;
        bool cache_qos;
        bool numa;
        int scratchpad_prefetch_mode;
    };

    struct CpuConfig {
        bool enabled;
        bool huge_pages;
        bool huge_pages_jit;
        std::optional<bool> hw_aes;
        std::optional<int> priority;
        bool memory_pool;
        bool yield;
        int max_threads_hint;
        bool asm_enabled;
        std::optional<std::string> argon2_impl;
        bool cn_0;
        bool cn_lite_0;
    };

    struct OpenCLConfig {
        bool enabled;
        bool cache;
        std::optional<std::string> loader;
        std::string platform;
        bool adl;
        bool cn_0;
        bool cn_lite_0;
    };

    struct CudaConfig {
        bool enabled;
        std::optional<std::string> loader;
        bool nvml;
        bool cn_0;
        bool cn_lite_0;
    };

    struct PoolConfig {
        std::optional<std::string> algo;
        std::optional<std::string> coin;
        std::string url;
        std::string user;
        std::string pass;
        std::optional<std::string> rig_id;
        bool nicehash;
        bool keepalive;
        bool enabled;
        bool tls;
        std::optional<std::string> tls_fingerprint;
        bool daemon;
        std::optional<std::string> socks5;
        std::optional<std::string> self_select;
        bool submit_to_origin;

    struct TlsConfig {
        bool enabled;
        std::optional<std::string> protocols;
        std::optional<std::string> cert;
        std::optional<std::string> cert_key;
        std::optional<std::string> ciphers;
        std::optional<std::string> ciphersuites;
        std::optional<std::string> dhparam;
    };

    struct DnsConfig {
        int ip_version;
        int ttl;
    };

public:
    struct terminal1
    {
        
    };

    void write_file(const std::string& path, const std::string& text){
        std::ofstream file(path);

        file << text;
    
        file.close();
    }  

    std::variant<terminal1,std::string>load_json(const std::string& path){
        std::ifstream file(path);

        if(!file.is_open()){

            std::string L;

            L = std::string("ERROR: ") + std::string(std::strerror(errno));

            return L;
        }
        json j;

        file >> j;

        
    }
};