software_output = {
    "_links": {
               "self": {
                        "href": "https://localhost:9999/litp/rest/v1/software"
                    },
               "item-type": {
                        "href": "https://localhost:9999/"
                                "litp/rest/v1/item-types/software"
                        }
               },
    "_embedded": {
        "item": [
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/"
                                            "litp/rest/v1/software/items"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                    "item-types/software-item"
                                    }
                           },
                "id": "items",
                "item-type-name": "software-item",
                "state": "Initial"
            },
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/"
                                            "litp/rest/v1/software/deployables"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/deployable-entity"
                                    }
                           },
                "id": "deployables",
                "item-type-name": "deployable-entity",
                "state": "Initial"
            },
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/"
                                            "litp/rest/v1/software/profiles"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/profile"
                                    }
                           },
                "id": "profiles",
                "item-type-name": "profile",
                "state": "Initial"
            },
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/"
                                            "litp/rest/v1/software/runtimes"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/runtime-entity"
                                    }
                           },
                "id": "runtimes",
                "item-type-name": "runtime-entity",
                "state": "Initial"
            }
        ],
    },
    "id": "software",
    "item-type-name": "software",
    "state": "Initial",
    "properties": {},
    "messages": []
}

ms_ipaddresses_first_output = {
    "_links": {
               "self": {
                        "href": "https://localhost:9999/"
                        "litp/rest/v1/ms/ipaddresses"
                    },
               "item-type": {
                        "href": "https://localhost:9999/"
                                "litp/rest/v1/item-types/ip-range"
                        }
               },
    "_embedded": {
        "item": [
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/"
                                            "litp/rest/v1/ms/ipaddresses/ip1"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/ip-range"
                                    }
                           },
                "id": "ip1",
                "item-type-name": "ip-range",
                "state": "Initial"
            }
        ],
    },
    "id": "ipaddresses",
    "item-type-name": "ip-range",
    "state": "Initial",
    "properties": {},
    "messages": []
}

ms_ipaddresses_second_output = {
    "_links": {
               "self": {
                        "href": "https://localhost:9999/"
                        "litp/rest/v1/ms/ipaddresses/ip1"
                    },
               "item-type": {
                        "href": "https://localhost:9999/"
                                "litp/rest/v1/item-types/ip-range"
                        }
               },
    "_embedded": {},
    "id": "ip1",
    "item-type-name": "ip-range",
    "state": "Initial",
    "properties": {
        "address": "10.10.10.100",
        "network_name": "nodes"
    },
    "messages": []
}

invalid_location_output = {
    "messages": [
        {
            "_links": {
                    "self": {
                            "href": "https://localhost:9999/litp/rest/v1/"
                                    "invalid"
                            }
                       },
            "type": "InvalidLocationError",
            "message": "Item not found",
         }
    ]
}

create_response = {
    "_links": {
           "self": {
                    "href": "https://localhost:9999/litp/rest/v1"
                            "/software/profiles"
                },
           "item-type": {
                    "href": "https://localhost:9999/litp/rest/v1"
                            "/item-types/profile"
                    }
           },
    "_embedded": {
        "item": [
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/litp/rest/"
                                            "v1/software/profiles/rhel_6_4"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/os-profile"
                                    }
                           },
                "id": "rhel_6_4",
                "item-type-name": "os-profile",
                "state": "Initial"
            },
            {
                "_links": {
                           "self": {
                                    "href": "https://localhost:9999/litp/rest/"
                                            "v1/software/profiles/rhel_6_5"
                                    },
                           "item-type": {
                                    "href": "https://localhost:9999/"
                                            "item-types/os-profile"
                                    }
                           },
                "id": "rhel_6_5",
                "item-type-name": "os-profile",
                "state": "Initial"
            }

        ],
    },
    "id": "profiles",
    "item-type-name": "profile",
    "state": "Initial",
    "properties": {},
    "messages": []
}

create_response_from_alt_url = {
    "_links": {
           "self": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "/software/profiles"
                },
           "item-type": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "/item-types/profile"
                    }
           },
    "_embedded": {
        "item": [
            {
                "_links": {
                           "self": {
                                    "href": "https://alt_ms1:9999/litp/rest/"
                                            "v1/software/profiles/rhel_6_5"
                                    },
                           "item-type": {
                                    "href": "https://alt_ms1:9999/"
                                            "item-types/os-profile"
                                    }
                           },
                "id": "rhel_6_5",
                "item-type-name": "os-profile",
                "state": "Initial"
            },
            {
                "_links": {
                           "self": {
                                    "href": "https://alt_ms1:9999/litp/rest/"
                                            "v1/software/profiles/rhel_6_5"
                                    },
                           "item-type": {
                                    "href": "https://alt_ms1:9999/"
                                            "item-types/os-profile"
                                    }
                           },
                "id": "rhel_6_5",
                "item-type-name": "os-profile",
                "state": "Initial"
            }

        ],
    },
    "id": "profiles",
    "item-type-name": "profile",
    "state": "Initial",
    "properties": {},
    "messages": []
}

create_fail_response = {
    "messages": [
        {
            "_links":{
                      "self": {
                               "href": "https://localhost:9999/litp/rest/v1/"
                                       "software/badbranch/profile"
                               }
                      },
            "type": "InvalidLocationError",
            "message": "Path not found",
        }
    ]
}

update_output = {
    "_links": {
           "self": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "deployments/single_blade/clusters/cluster1/"
                            "nodes/node1/ipaddresses/ip1"
                    },
           "item-type": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "/item-types/ip-range"
                    }
    },
    "_embedded": {},
    "id": "ip1",
    "item-type-name": "ip-range",
    "state": "Initial",
    "properties": {
                   "address": "10.10.10.10",
                   "network_name": "test_network"
                   },
    "messages": []
}

inherit_output = {
    "_links": {
        "self": {
                 "href": "https://ms1:9999/litp/rest/v1/deployments"
                         "/single_blade/nodes/node1/system"
                         },
        "item-type": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "/item-types/system"
                    }
    },
    "_embedded": {},
    "id": "system",
    "item-type-name": "libvirt-system",
    "state": "Initial",
    "properties": {
                   "system_name": "VM1"
                   },
    "messages": [],
}

create_deployment_response = {
    "_links": {
        "self": {
                 "href": "https://localhost:9999/litp/rest/v1/deployments/dep1"
                },
        "item-type": {
                    "href": "https://alt_ms1:9999/litp/rest/v1"
                            "/item-types/deployment"
                    }
    },
    "_embedded": {
        "item": [
                 {
                "_links": {
                           "self": {
                                    "href": "https://alt_ms1:9999/litp/rest/"
                                            "v1/deployments/dep1/clusters"
                                    },
                           "item-type": {
                                    "href": "https://alt_ms1:9999/"
                                            "item-types/cluster"
                                    }
                           },
                "id": "clusters",
                "item-type-name": "cluster",
                "state": "Initial",
                "properties": {},
                }
        ],
    },
    "id": "dep1",
    "item-type-name": "deployment",
    "state": "Initial",
    "properties": {},
    "messages": []
}

plan_output = """
{
    "_links": {
               "self": {
                        "href": "https://localhost:9999/litp/rest/v1/plans/plan"
                },
               "item-type": {
                        "href": "https://alt_ms1:9999/litp/rest/v1/item-types/plan"
                }
    },
    "_embedded": {
      "item": [
               {
              "_links": {
                    "self": {
                             "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases"
                    },
                    "collection-of": {
                            "href": "https://alt_ms1:9999/litp/rest/v1/item-types/phase"
                    }
                },
              "_embedded": {
              "item": [
                  {
                      "_links": {
                            "self": {
                                     "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/1"
                            },
                            "type": {
                                    "href": "https://alt_ms1:9999/litp/rest/v1/item-types/phase"
                            }
                        },
                      "_embedded": {
                      "item":[
                              {
                                  "_links": {
                                        "self": {
                                                 "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/1/tasks"
                                        },
                                        "collection-of": {
                                                "href": "https://localhost:9999/litp/rest/v1/item-types/task"
                                        }
                                    },
                                  "_embedded": {
                                  "item":[
                                                 {
                                              "_links": {
                                                    "self": {
                                                             "href": "https://localhost:9999/litp/rest/v1/plans/plan/phases/1/tasks/a_mock_task"
                                                    },
                                                    "type": {
                                                            "href": "https://localhost:9999/litp/rest/v1/item-types/task"
                                                    },
                                                    "rel": {
                                                            "href": "https://localhost:9999/litp/rest/v1/ms"
                                                    }
                                                },
                                                "id": "a_mock_task",
                                                "item-type-name": "task",
                                                "state": "Initial",
                                                "description": "Mock task done on node2",
                                                "call_id": "node2",
                                                "call_type": "hosts::hostentry"
                                            }
                                    ]
                                    },
                                    "id": "1",
                                    "item-type-name": "collection-of-task",
                                    "state": "Initial",
                                    "properties": {}
                            }
                        ]
                        },
                        "id": "1",
                        "item-type-name": "phase",
                        "state": "Initial",
                        "properties": {}
                    }
                ]
                },
                "id": "phases",
                "item-type-name": "collection-of-phase",
                "state": "Initial",
                "properties": {}
                }
            ]
    },
    "id": "plan",
    "item-type-name": "plan",
    "properties": {"state": "initial"},
    "messages": []
}
"""

recursive_ms_output = """
{
    "_links": {
               "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms"
                    },
               "item-type": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/item-types/ms"
                    }
     },
    "_embedded": {
        "item": [
            {
                "_links": {
                    "self": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/ms/services"
                        },
                    "item-type": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/item-types/ms-service"
                        }
                },
                "require": "network_profile",
                "id": "services",
                "item-type-name": "collection of ms-service",
                "state": "Initial",
                "properties": {},
                "messages": []
            },
            {
                "_links": {
                    "self": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/ms/items"
                        },
                    "item-type": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/item-types/software-item"
                        }
                },
                "id": "services",
                "item-type-name": "collection of software-items",
                "state": "Initial",
                "properties": {},
                "messages": []
            },
            {
                "_links": {
                    "self": {
                        "href":
                           "https://localhost:9999/litp/rest/v1/ms/ipaddresses"
                        },
                    "item-type": {
                        "href":
                            "https://localhost:9999/litp/rest/v1/item-types/ip-range"
                        }
                },
                "_embedded": {
                    "item": [
                        {
                            "_links": {
                                       "self": {
                                                "href": "https://localhost:9999/litp/rest/v1/ms/ipaddresses/ip1"
                                                },
                                       "item-type": {
                                                "href": "https://localhost:9999/item-types/ip-range"
                                                }
                                       },
                            "id": "ip1",
                            "item-type-name": "ip-range",
                            "state": "Initial"
                        }
                    ]
                },
                "id": "ipaddresses",
                "item-type-name": "collection of ip-range",
                "state": "Initial",
                "properties": {},
                "messages": []
            }
        ]
    },
    "id": "ms",
    "item-type-name": "ms",
    "state": "Initial",
    "properties": {
        "hostname": "ms1"
    },
    "messages": []
}
"""

ms_output = """
{
    "_links": {
            "self": {
                "href": "https://localhost:9999/litp/rest/v1/ms"
                    },
            "item-type": {
                "href":
                    "https://localhost:9999/litp/rest/v1/item-types/ms"
                        }
    },
    "_embedded": {
        "item": [
            {
                "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/ms/services"
                                },
                        "item-type": {
                            "href": "https://localhost:9999/litp/rest/v1/item-types/ms-service"
                                    }
                },
                "id": "services",
                "state": "Initial",
                "item-type-name":  "ms-service"
            },
            {
                "_links": {
                        "self": {
                            "href":
                                "https://localhost:9999/litp/rest/v1/ms/items"
                                },
                        "item-type": {
                            "href": "https://localhost:9999/litp/rest/v1/item-types/software-item"
                                    }
                },
                "id": "items",
                "state": "Initial",
                "item-type-name":  "software-items"
            },
            {
                "_links": {
                        "self": {
                            "href":
                                "https://localhost:9999/litp/rest/v1/ms/ipaddresses"
                                },
                        "item-type": {
                            "href": "https://localhost:9999/litp/rest/v1/item-types/ip-range"
                                    }
                },
                "id": "ipaddresses",
                "state": "Initial",
                "item-type-name":  "ip-range"
            }
        ]
    },
    "id": "ms",
    "item-type-name": "ms",
    "state": "Initial",
    "properties": {
        "hostname": "ms1"
    },
    "messages": []
}
"""

item_types_output = """
{
    "_links": {
            "self": {
                "href": "https://localhost:9999/litp/rest/v1/item-types"
                    }
    },
    "_embedded": {
        "item-type": [
        {
            "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/volume-group"
                       }
            },
            "id": "volume-group",
            "description": ""
        },
        {
            "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/profile"
                    }
            },
            "id": "profile",
            "description": "Base profile item."
        }
        ]
    },
    "id": "item-types",
    "messages": []
}
"""

property_types_output = """
{
    "_embedded": {
                "property-type": [
            {
                "_links": {
                        "self": {
                             "href": "https://localhost:9999/litp/rest/v1/porperty_types/ipv6_address"
                                }
                 },
                "id": "ipv6_address",
                "regex": "^.*$"
            },
            {
                "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/porperty_types/selinux_mode"
                                }
                },
                "id": "selinux_mode",
                "regex": "^(enforcing|permissive|disabled)$"
            }
        ]
    },
    "id": "property-types",
    "messages": []
}
"""

deployments_output = """
{
    "_links": {
            "self": {
                "href": "https://localhost:9999/litp/rest/v1/deployments"
                    },
            "item-type": {
                "href":
                    "https://localhost:9999/litp/rest/v1/item-types/deployment"
                        }
    },
    "_embedded": {
          "item": [
                {
                "_links": {
                        "self": {
                            "href": "https://localhost:9999/litp/rest/v1/deployments/dep1"
                        },
                        "item-type": {
                            "href": "https://localhost:9999/litp/rest/v1/item-types/deployment"
                        }
                },
                "id": "dep1",
                "item-type-name": "deployment",
                "state": "Initial"
                }
            ]
    },
    "id": "dep1",
    "item-type-name": "deployment",
    "state": "Initial",
    "properties": [],
    "messages": []
}
"""

create_plan_error_output = """
{
    "messages": [
        {
            "_links":{
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/deployments/local_vm/clusters/cluster1/nodes/node1"
                    }
            },
            "type": "MissingRequiredItemError",
            "message": "ItemType 'node' is required to have a 'reference' with id 'storage_profile' and type 'storage-profile-base'"
        }
    ]
}
"""

item_description = {
    "_links": {
               "self": {
                        "href": "https://localhost:9999/litp/rest/v1/"
                                "item-types/package-list"
                        }
               },
    "properties": {
                   "name": {
                        "_links": {
                            "self": {
                                            "href":
                                 "https://localhost:9999/litp/rest/v1/"
                                 "property_types/basic_string"
                            }
                        },
                        "default": None,
                        "required": False,
                        "description": ""
                   },
                   "version": {
                        "_links": {
                                "self": {
                                    "href":
                                       "https://localhost:9999/litp/rest/v1/"
                                       "property_types/basic_string"
                                }
                        },
                        "required": False,
                        "default": None,
                        "description": ""
                   }
    },
    "_embedded": {
                  "item": [
                    {
                        "_links": {
                                   "collection-of": {
                                            "href":
                                 "https://localhost:9999/litp/rest/v1/"
                                 "item-types/package"
                                    }
                        },
                        "id": "packages",
                        "max": 9999,
                        "min": 0,
                }
        ]
    },
    "name": "package-list",
    "base-type": {
        "name": "software-item",
        "href": "https://localhost:9999/litp/rest/v1/item-types/software-item"
    },
    "description": "Collection of software packages to install",
}

show_link_output = {
    "_links": {
               "self": {
                        "href": "https://localhost:9999/litp/rest/v1/"
                        "deployments/single_blade/clusters/cluster1/"
                        "nodes/node1/system"
                    },
               "reference-to": {
                        "href": "/infrastructure/system_providers/libvirt1/systems/vm1"
                    }

               },
    "_embedded": {
        "item": [],
    },
    "id": "system",
    "item-type-name": "libvirt-system",
    "state": "Initial",
    "properties": {
                   "system_name": "VM1"
    },
    "messages": []
}

show_inherited_output_no_properties = {
    "item-type-name": "reference-to-file-system",
    "state": "Initial",
    "_links": {
        "inherited-from": {
            "href": "https://localhost:9999/litp/rest/v1/infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root"
        },
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root"
        },
        "item-type": {
            "href": "https://localhost:9999/litp/rest/v1/item-types/file-system"
        }
    },
    "id": "root"
}

show_inherited_output_no_overwritten_properties = {
    "properties": {
        "mount_point": "/",
        "type": "ext4",
        "size": "48G"
    },
    "item-type-name": "reference-to-file-system",
    "state": "Initial",
    "_links": {
        "inherited-from": {
            "href": "https://localhost:9999/litp/rest/v1/infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root"
        },
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root"
        },
        "item-type": {
            "href": "https://localhost:9999/litp/rest/v1/item-types/file-system"
        }
    },
    "id": "root"
}

show_inherited_output = {
    "properties": {
        "mount_point": "/",
        "type": "ext4",
        "size": "48G"
    },
    "properties-overwritten": [
        "size"
    ],
    "item-type-name": "reference-to-file-system",
    "state": "Initial",
    "_links": {
        "inherited-from": {
            "href": "https://localhost:9999/litp/rest/v1/infrastructure/storage/storage_profiles/profile1/volume_groups/vg1/file_systems/root"
        },
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/deployments/deployment1/clusters/cluster1/nodes/node1/storage_profile/volume_groups/vg1/file_systems/root"
        },
        "item-type": {
            "href": "https://localhost:9999/litp/rest/v1/item-types/file-system"
        }
    },
    "id": "root"
}

show_completion_output = {
    "_embedded": {
        "item": [
            {
                "item-type-name": "ref-collection-of-software-item", 
                "state": "Initial", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/items"
                    }, 
                    "ref-collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/software-item"
                    }
                }, 
                "id": "items"
            }, 
            {
                "item-type-name": "collection-of-network-interface", 
                "state": "Applied", 
                "required": "os", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/network_interfaces"
                    }, 
                    "collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/network-interface"
                    }
                }, 
                "id": "network_interfaces"
            }, 
            {
                "item-type-name": "reference-to-system", 
                "state": "Applied", 
                "_links": {
                    "inherited-from": {
                        "href": "https://localhost:9999/litp/rest/v1/infrastructure/systems/sys1"
                    }, 
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/system"
                    }, 
                    "item-type": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/system"
                    }
                }, 
                "id": "system", 
                "properties": {
                    "system_name": "KVM_MS"
                }
            }, 
            {
                "item-type-name": "collection-of-ms-service", 
                "state": "Applied", 
                "required": "network_interfaces", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/services"
                    }, 
                    "collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/ms-service"
                    }
                }, 
                "id": "services"
            }, 
            {
                "item-type-name": "ref-collection-of-route-base", 
                "state": "Initial", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/routes"
                    }, 
                    "ref-collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/route-base"
                    }
                }, 
                "id": "routes"
            }, 
            {
                "item-type-name": "collection-of-node-config", 
                "state": "Initial", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/configs"
                    }, 
                    "collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/node-config"
                    }
                }, 
                "id": "configs"
            }, 
            {
                "item-type-name": "ref-collection-of-file-system-base", 
                "state": "Initial", 
                "_links": {
                    "self": {
                        "href": "https://localhost:9999/litp/rest/v1/ms/file_systems"
                    }, 
                    "ref-collection-of": {
                        "href": "https://localhost:9999/litp/rest/v1/item-types/file-system-base"
                    }
                }, 
                "id": "file_systems"
            }
        ]
    }, 
    "id": "ms", 
    "item-type-name": "ms", 
    "state": "Applied", 
    "_links": {
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/ms"
        }, 
        "item-type": {
            "href": "https://localhost:9999/litp/rest/v1/item-types/ms"
        }
    }, 
    "properties": {
        "hostname": "virt-ms"
    }
}

prepare_restore_output = {
    "id": "prepare-restore",
    "item-type-name": "prepare-restore",
    "state": "Initial",
    "_links": {
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/litp/prepare-restore"
        },
        "item-type": {
            "href": "https://localhost:9999/litp/rest/v1/item-types/prepare-restore"
        }
    },
    "properties": {
        "path": "/",
        "actions": "all"
    }
}

prepare_restore_validation_error_output = {   
    "_links": {
        "self": {
            "href": "https://localhost:9999/litp/rest/v1/litp/prepare-restore"
        }
    },
    "messages": [
        {   
            "message": "Invalid value '/invalid_path'.",
            "type": "ValidationError",
            "property_name": "path"
        }
    ]
}

