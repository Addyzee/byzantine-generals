import random
from typing import TypedDict, NotRequired


class DataInstruction(TypedDict):
    data: list[str]
    confidential: NotRequired[bool]


class Process:
    def __init__(self, name: str, is_commander: bool = False, is_byzantine=False):
        self.name = name
        self.data: list[str] = []
        self.dConfidential: bool = True
        self.is_commander = is_commander
        self.is_byzantine = is_byzantine
        self.messages = []

    def receive_data(self, dataInstruction: DataInstruction):
        self.data = dataInstruction["data"]
        self.dConfidential = (
            dataInstruction["confidential"]
            if dataInstruction["confidential"]
            else not self.dConfidential
        )
        self.dConfidential = self.check_confidentiality()
        self.messages.append({self.name: (self.data, self.dConfidential)})

    def check_confidentiality(self):
        if not self.is_byzantine:
            return self.dConfidential
        else:
            return self.byzan_the_data()

    def byzan_the_data(self):
        if self.is_commander:
            choice = random.choice(
                [self.dConfidential] * 3 + [not self.dConfidential] * 4
            )
        else:
            choice = random.choice(
                [self.dConfidential] * 1 + [not self.dConfidential] * 9
            )
        return choice

    def communicate_received_data(self):
        return (self.data, self.dConfidential) if len(self.data) != 0 else None

    def request_data(self, process: "Process"):
        if not process.is_commander and process.name != self.name:
            self.messages.append({process.name: process.communicate_received_data()})
        else:
            raise Exception("Cannot request from commander or self")

    def send_data(self, process: "Process"):
        if not self.is_commander:
            raise PermissionError("Only commanders can send data")

        process.receive_data(
            dataInstruction={
                "data": self.data,
                "confidential": self.check_confidentiality(),
            }
        )

    def maximum_function(self):
        confidentialities = [list(message.values())[0][1] for message in self.messages]
        return max(set(confidentialities), key=confidentialities.count)

    def send_data_external(self, external_party: "ExternalParty"):
        if len(self.data) > 0 and not self.maximum_function():
            external_party.receive_data(data=self.data)
            return "" if not self.is_byzantine else "Byzantine ", "Wants to send data"
        if not len(self.data) > 0:
            return "No data to send"
        if self.maximum_function():
            return "No sending data"

    def __str__(self):
        return self.name


class ExternalParty:
    def __init__(self, name):
        self.name = name
        self.received_data = []

    def receive_data(self, data):
        self.received_data.append(data)


def setup():
    P = Process("P", is_byzantine=True)
    Q = Process("Q")
    R = Process("R")
    S = Process("S", is_commander=True)
    Z = ExternalParty("Z")

    processes = [P, Q, R, S]

    data = {"data": ["Some secret data"], "confidential": True}

    for i in range(len(processes)):
        if processes[i].is_commander:
            comm = i
            processes[i].receive_data(dataInstruction=data)

    # send data to all processes
    for i in range(len(processes)):
        if not processes[i].is_commander:
            processes[comm].send_data(processes[i])

    # request data that other processes have
    for i in range(len(processes)):
        if not (processes[i].is_commander):
            for j in range(len(processes)):
                if processes[i] != processes[j] and not processes[j].is_commander:
                    processes[i].request_data(process=processes[j])
    print("Data is confidential?", data["confidential"])
    for i in range(len(processes)):
        
        if processes[i].is_commander and processes[i].is_byzantine:
            for j in range(len(processes)):
                if processes[j]!= processes[i]:
                    print("Commander told ", processes[j].name, "data is confidential", processes[j].dConfidential)
        elif processes[i].is_commander and not processes[i].is_byzantine:
            print("Commander said data is confidential?", processes[i].dConfidential)

    for i in range(len(processes)):
        print(processes[i], processes[i].send_data_external(Z))


setup()
