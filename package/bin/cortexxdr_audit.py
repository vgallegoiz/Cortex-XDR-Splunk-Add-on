import json
import logging
import sys
import datetime

import import_declare_test
from solnlib import conf_manager, log
from solnlib.modular_input import checkpointer
from splunklib import modularinput as smi

from CortexXDRObject import CortexXDR

ADDON_NAME = "cortexxdr_audit"

def logger_for_input(input_name: str) -> logging.Logger:
    return log.Logs().get_logger(f"{ADDON_NAME.lower()}_{input_name}")

def get_account_info(session_key: str, account_name: str):
    cfm = conf_manager.ConfManager(
        session_key,
        ADDON_NAME,
        realm=f"__REST_CREDENTIAL__#{ADDON_NAME}#configs/conf-cortexxdr_audit_account",
    )
    account_conf_file = cfm.get_conf("cortexxdr_audit_account")
    api_key = account_conf_file.get(account_name).get("api_key")
    api_id = account_conf_file.get(account_name).get("api_key_id")
    tenant_name = account_conf_file.get(account_name).get("tenant_name")
    region = account_conf_file.get(account_name).get("region")
    return api_id, api_key, tenant_name, region

class Input(smi.Script):
    def __init__(self):
        super().__init__()

    def create_or_return_checkpointer(self):
        session_key = self._input_definition.metadata["session_key"]
        self.checkpoint = checkpointer.KVStoreCheckpointer(f"{ADDON_NAME}_checkpointer", session_key, ADDON_NAME, )

    def get_scheme(self):
        scheme = smi.Scheme("cortexxdr_audit")
        scheme.description = "cortexxdr_audit input"
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False
        #scheme.add_argument(smi.Argument("name", title="Name", description="Name", required_on_create=True))        
        return scheme

    def validate_input(self, definition: smi.ValidationDefinition):
        return

    def stream_events(self, inputs: smi.InputDefinition, event_writer: smi.EventWriter):
        # inputs.inputs is a Python dictionary object like:
        # {
        #   "prisma_inputs_ucc://<input_name>": {
        #     "account": "<account_name>",
        #     "disabled": "0",
        #     "host": "$decideOnStartup",
        #     "index": "<index_name>",
        #     "interval": "<interval_value>",
        #     "python.version": "python3",
        #   },
        # }
        for input_name, input_item in inputs.inputs.items():
            normalized_input_name = input_name.split("/")[-1]
            logger = logger_for_input(normalized_input_name)

            try:
                session_key = self._input_definition.metadata["session_key"]
                log_level = conf_manager.get_log_level(
                    logger=logger,
                    session_key=session_key,
                    app_name=ADDON_NAME,
                    conf_name=f"{ADDON_NAME}_settings",
                )
                logger.setLevel(log_level)
                log.modular_input_start(logger, normalized_input_name)
                logger.info("Starting checkpointer")
                self.create_or_return_checkpointer()
                
                logger.info("getting account info")
                api_id, api_key, tenant_name, region = get_account_info(session_key, input_item.get("account"))
                index = input_item.get("index")
                input_types = input_item.get("input_type", "").split('|')
                input_type_log = ",".join(input_types)
                logger.info(f"input_type={input_type_log} index={index} tenant={tenant_name}")

                logger.info(f"Initializing CortexXDR: tenant={tenant_name}, region={region}")
                cortex = CortexXDR(api_key=api_key, api_key_id=api_id, tenant_name=tenant_name, region=region)
                if "management_logs" in input_types:
                    try:
                        logger.info("Getting checkpointer for management_logs")
                        last_checkpoint = self.checkpoint.get(f"{tenant_name.lower()}_management_logs")
                        start_time = int()
                        if last_checkpoint is None:
                            logger.info("There is no checkpointer on management_logs")
                            start_time = int(datetime.datetime.now().timestamp() * 1000) # already in epoch ms
                        else:
                            start_time = int(last_checkpoint)  # already in epoch ms

                        logger.info("Fetching Cortex XDR management_logs...")
                        response = cortex.get_audit_management_logs(start_time=start_time)
                        try:
                            data = response.json()
                        except Exception as e:
                            logger.error("No hay JSON")
                            raise Exception
                        now = datetime.datetime.now().timestamp()
                        if response.status_code == 200 and data["reply"]["result_count"] != 0:
                            for item in data['reply']['data']:
                                item.update({'tenant': tenant_name, 'region': region})
                                event = smi.Event(time="%.3f" % now, sourcetype="cortex:management_logs", index=index, source=tenant_name)
                                event.stanza = input_name
                                event.data = json.dumps(item, ensure_ascii=False, default=str)
                                event_writer.write_event(event)
                                logger.info("Management logs successfully ingested.")
                        elif response.status_code == 200 and data["reply"]["result_count"] == 0:
                            logger.info(f"No data in management_logs to ingest on {tenant_name} with {data}")
                        else:
                            logger.info(f"{response.status_code} with {data}")
                        self.checkpoint.update(f"{tenant_name.lower()}_management_logs", str(int(now) * 1000))
                        logger.info(f"Checkpointer on {tenant_name} and sourcetyepe agents_reports updated")
                    except Exception as e:
                        logger.info("Fallo en get response")
                        log.log_exception(logger, e, exc_label=ADDON_NAME ,msg_before=f'client={tenant_name}')

                if "agents_reports" in input_types:
                    try:
                        logger.info("Getting checkpointer for agents_reports")
                        last_checkpoint = self.checkpoint.get(f"{tenant_name.lower()}_agents_reports")
                        start_time = int()
                        if last_checkpoint is None:
                            logger.info("There is no checkpointer on agents_reports")
                            start_time = int(datetime.datetime.now().timestamp() * 1000) # already in epoch ms
                        else:
                            start_time = int(last_checkpoint)  # already in epoch ms

                        logger.info("Fetching Cortex XDR agents_reports...")
                        response = cortex.get_audit_agent_logs(start_time=start_time)
                        try:
                            data = response.json()
                        except Exception as e:
                            logger.error("No hay JSON")
                            raise Exception
                        now = datetime.datetime.now().timestamp()
                        if response.status_code == 200 and data["reply"]["result_count"] != 0:
                            for item in data['reply']['data']:
                                item.update({'tenant': tenant_name, 'region': region})
                                event = smi.Event(time="%.3f" % now, sourcetype="cortex:agents_reports", index=index, source=tenant_name)
                                event.stanza = input_name
                                event.data = json.dumps(item, ensure_ascii=False, default=str)
                                event_writer.write_event(event)
                                logger.info("Agent reports logs successfully ingested.")
                        elif response.status_code == 200 and data["reply"]["result_count"] == 0:
                            logger.info(f"No data in agent_reports to ingest on {tenant_name} with {data}")
                        else:
                            logger.info(f"{response.status_code} with {data}")
                        self.checkpoint.update(f"{tenant_name.lower()}_agents_reports", str(int(now) * 1000))
                        logger.info(f"Checkpointer on {tenant_name} and sourcetyepe agents_reports updated")
                    except Exception as e:
                        logger.info("Fallo en get response")
                        log.log_exception(logger, e, exc_label=ADDON_NAME ,msg_before=f'client={tenant_name}')
                log.modular_input_end(logger, normalized_input_name)

            except Exception as e:
                logger.info(f"Error during Cortex XDR ingestion {e}")
                log.log_exception(logger, e, exc_label=ADDON_NAME, msg_before="Error during Cortex XDR ingestion")

if __name__ == "__main__":
    exit_code = Input().run(sys.argv)
    sys.exit(exit_code)