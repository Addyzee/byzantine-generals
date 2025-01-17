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
            choice = random.choice([self.dConfidential, not self.dConfidential])
        else:
            print(self.dConfidential, not self.dConfidential)
            choice = random.choice(
                [self.dConfidential] * 1 + [not self.dConfidential] * 9
            )
            print(choice)
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
        self.dConfidential = self.check_confidentiality()
        process.receive_data(
            dataInstruction={
                "data": self.data,
                "confidential": self.dConfidential,
            }
        )

    def maximum_function(self):
        confidentialities = [list(message.values())[0][1] for message in self.messages]
        max_choice = max(set(confidentialities), key=confidentialities.count)
        return not max_choice if self.is_byzantine else max_choice

    def send_data_external(self, external_party: "ExternalParty"):
        if len(self.data) > 0 and not self.maximum_function():
            external_party.receive_data(data=self.data)
            return ("Wants to send data", True)
        if not len(self.data) > 0:
            return ("No data to send", False)
        if self.maximum_function():
            return ("No sending data", False)

    def __str__(self):
        return self.name


class ExternalParty:
    def __init__(self, name):
        self.name = name
        self.received_data = []

    def receive_data(self, data):
        self.received_data.append(data)


def make_decision(outcomes: list[str]):
    return max(set(outcomes), key=outcomes.count)


def setup():
    P = Process("P", is_byzantine=True, is_commander=True)
    Q = Process("Q")
    R = Process("R")
    S = Process("S")
    Z = ExternalParty("Z")

    processes = [P, Q, R, S]

    data = {"data": ["Some secret data"], "confidential": True}

    start = input("Input X for commander to retrieve data from database\n")
    if start:
        for i in range(len(processes)):
            if processes[i].is_commander:
                comm = i
                processes[i].receive_data(dataInstruction=data)

        print("Data sent to commander", data)

    start = input("Input X for commander to send data to other processes\n")
    if start:
        # send data to all processes
        for i in range(len(processes)):
            if not processes[i].is_commander:
                processes[comm].send_data(processes[i])
                print(
                    "Commander tells process",
                    processes[i].name,
                    "that data is confidential? ",
                    processes[comm].dConfidential,
                )

    start = input("Input X to initiate RPC to receive data from other processes\n")
    if start:
        # request data that other processes have
        for i in range(len(processes)):
            if not (processes[i].is_commander):
                for j in range(len(processes)):
                    if processes[i] != processes[j] and not processes[j].is_commander:
                        processes[i].request_data(process=processes[j])
                print(
                    "Total information with process",
                    processes[i],
                    ":",
                    processes[i].messages,
                )

    # check decision on whether to send data to external party
    start = input("Input X to check for consensus\n")
    if start:
        outcomes = [processes[i].send_data_external(Z) for i in range(len(processes))]
        outcomeBools = [outcome[1] for outcome in outcomes]
        for i in range(len(processes)):
            print(
                processes[i],
                outcomes[i][0],
                ("(Hint: is byzantine)" if processes[i].is_byzantine else ""),
            )
    print(
        "Decision is to ",
        ("send data " if make_decision(outcomes=outcomeBools) else "not send data"),
    )


setup()
