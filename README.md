# Database Special Agent
Agent DB is a Checkmk special agent that enables direct monitoring of various database systems via network connections—without the need to deploy any Checkmk agent plugin on the database hosts.

## 🔍 Overview
This special agent can simplify monitoring setups by directly connecting to supported databases over the network. It leverages custom host attributes for flexible configuration and clean integration into Checkmk environments.

## Supported Database Backends
- Oracle
- Microsoft SQL Server (MSSQL)
- PostgreSQL
- MySQL

## Key Features
- One Checkmk GUI Setup Rule which allows to configure all supported Database backends.
- Agentless Monitoring: No need to install a Checkmk agent on database hosts.
- Network-Based Access: Connects using the native database protocols, over TCP/IP.
- Custom Host Attributes: Easily configure ports, SIDs, or other connection details using host attributes in Checkmk.
- Security-Conscious: Ideal for environments where local agent and plugin installation is restricted.

## Thanks to:
LHM (Landeshauptstadt Muenchen): This Checkmk Special Agent was developed in cooperation with the "Eigenbetrieb it@M" of the City of Munich.

- Maximilian Sachmann & Sebastian Böhm for perfect requirements engineering and testing.
- Konstantin Büttner as a first-class co-developer with great ideas.