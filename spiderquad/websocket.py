from twisted.internet import protocol, reactor, endpoints
import json

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        j = json.loads(data)
        print(j)
        self.transport.write(data)

class EchoFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

endpoints.serverFromString(reactor, "tcp:8000").listen(EchoFactory())
reactor.run()
