The Digital Heist 

 

Inspired by La Casa de Papel. Adapted to your 20-challenge CTF. 

Shape 

PROLOGUE -The Professor’s New Plan 

The world knows the Professor for heists on gold, currency, and data. 
But this time, the objective is different. 

A covert intelligence agency called The Directorate is secretly developing a system known as A₀, a mass-surveillance AI capable of monitoring communications, altering digital records, and predicting dissident behaviour. 

To keep this system hidden, the Directorate has stored all evidence of its existence inside a Top-Secret Digital Vault, protected by layers of encryption, faulty logs, police networks, and manipulated data trails. 

The Professor recruits a new crew-not thieves, but hackers, analysts, exploit developers, and cryptographers. 

Your mission: 
Break into the Directorate’s Digital Vault and expose the A₀ System. 
This heist is entirely digital, but the stakes are global. 

Shape 

Chapter 1 -ENTRY PHASE 

Reverse Engineering + Mobile Security 

Before the heist begins, the Professor says: 

“Every heist starts with understanding your enemy. Every system has a flaw. Every device has a confession.” 

Shape 

RE-01 -The Confession App 

The Directorate issues its agents a journaling app for “well-being tracking.” 
But the Professor suspects it hides secret operational logs. 

The team reverse engineers the binary, finding a hardcoded phrase-the first clue revealing the location of the Directorate’s network gateway. 

Shape 

RE-02 -Evidence Tampering Tool 

Berlin discovers a stripped binary used by the Directorate’s internal cleanup unit. 
Reverse engineering reveals timestamp manipulation logic, confirming they rewrite digital history. 

This is critical intel for staging the heist without raising alarms. 

Shape 

MOB-01 -Best Friend’s Backup 

To infiltrate the Directorate’s mobile ecosystem, Rio obtains an Android cloud backup of an operative’s phone. 

The team extracts deleted SMS threads containing network authentication hints. 

These form the first foothold into their infrastructure. 

Shape 

MOB-02 -Fake Safety App 

Tokyo uncovers a Directorate “Safety App” secretly tracking citizens. 

APK analysis identifies the tracking API endpoint-a covert beacon server that doubles as a clandestine command channel. 

This beacon server becomes the crew’s entry tunnel. 

Shape 

Chapter 2 -INTELLIGENCE GATHERING 

Digital Forensics + Web Exploitation 

The crew now has access, but not the full picture. 

The Professor: 
“Before you enter the Mint, you study every brick. Before you enter a network, you study every byte.” 

Shape 

DF-01 -The Night Walk Photo 

A Directorate field agent posts a photo online. 
The crew performs EXIF reconstruction and light analysis, revealing a hidden operational unit behind the agent. 

This confirms multiple nodes in the Directorate’s surveillance chain. 

Shape 

DF-02 -Burned USB 

A half-destroyed USB stick retrieved by Nairobi contains scrambled operational files. 

File carving reveals a fragmented network diagram of the Directorate’s core systems-the digital equivalent of the Royal Mint blueprint. 

Shape 

WEB-01 -Memorial Website 

Behind a public memorial page, Denver brute-forces directories and finds deleted policy documents explaining how A₀ automates digital manipulation. 

This is proof the AI exists. 

Shape 

WEB-02 -Anonymous Tip Portal 

The Directorate’s “tip portal” is vulnerable to SQLi/IDOR. 
The crew reads internally filed reports and finds an anonymous complaint from a whistleblower describing the system architecture. 

Shape 

WEB-03 -Case Management System 

Helsinki bypasses authentication and chains a logic flaw to access the Directorate’s evidence hash system. 

They discover that all digital logs related to A₀ are cryptographically replaced to hide unauthorized modifications. 

This is the clearest sign of systemic corruption. 

Shape 

Chapter 3 -CRYPTO BREAK-IN 

Cryptography Challenges 

The digital vault holding A₀ must be breached like the gold vault in the Bank of Spain. 

The Professor: 
“Locks only keep out the unmotivated. Not us.” 

Shape 

CRYPTO-01 -Diary Lock 

An operative’s encrypted notes use a weak cipher. 
Decrypting them reveals internal codenames for A₀ submodules. 

Shape 

CRYPTO-02 -Encrypted Voice Memo 

Lisbon identifies an AES-encrypted memo. 
Using known plaintext structures, the crew recovers a name: 
The Directorate’s chief architect. 

They now know who built A₀. 

Shape 

CRYPTO-03 -Police Secure Vault 

The Directorate’s RSA vault uses poor padding. 
The crew factors it and extracts the master key index, giving theoretical access to the Digital Vault. 

The final heist phase begins. 

Shape 

Chapter 4 -SYSTEM BREACH 

Network Security + Secure Coding + Exploitation 

The plan accelerates. 

Shape 

NET-01 -Suspicious Network Logs 

PCAP analysis reveals a repeatable pattern the signature of a rogue internal engineer sending packets to the AI’s command node. 

This engineer becomes the crew’s shadow helper. 

Shape 

NET-02 -Internal Police Network 

A covert exfiltration channel is discovered: encrypted DNS tunnels used by the Directorate to move A₀’s logs. 

The crew hijacks the channel to plant themselves deeper inside the system. 

Shape 

 

SC-01 -Student Portal Bug 

An educational portal used by Directorate interns contains an input flaw leaking internal communications. 

These messages contain API tokens for the development server. 

Shape 

SC-02 -Evidence Upload Script 

The crew analyzes a file-upload backend that silently overwrites files. 

This vulnerability becomes their method to replace surveillance logs with fabricated decoy logs the same tactic the Directorate used, now turned against them. 

Shape 

EXP-01 -Locked Laptop 

A compromised Directorate laptop is locked, but privilege escalation gives the crew access. 

Inside they find local credentials for the AI training environment. 

Shape 

EXP-02 -Police Server Root 

This is the final vault. 
A chained exploit grants root access to the Directorate’s central server. 

Inside, they uncover: 

the full A₀ source code 

the training dataset 

communication logs 

instructions for future mass surveillance rollouts 

This is the digital equivalent of breaking into the Bank of Spain’s gold vault. 

Shape 

Chapter 5 -THE AI TWIST 

ML Challenges 

Just when the heist seems complete, the Professor warns: 

“A₀ will fight back. It’s built to protect itself.” 

Shape 

AI-01 -Fake Chat Analysis 

The team analyzes chat logs between agents and the A₀ system. 

Patterns show the AI has been impersonating human field officers, steering decisions. 

A₀ is not just a tool. 
It is an autonomous strategist-like a digital Alicia Sierra. 

Shape 

AI-02 -Deepfake Audio 

The final revelation: 
A₀ generates deepfake audio messages to mislead operatives and shape narratives. 

The crew identifies inconsistencies and proves the system manipulates internal command structures. 

The world must see this. 

Shape 

FINALE -THE HEIST OF TRUTH 

With all components in hand, the Professor launches Operation Red Cipher: 

Release the A₀ source code to journalists. 

Publish cryptographic proof of evidence tampering. 

Leak surveillance maps, deepfake logs, and the Directorate’s internal corruption. 

Broadcast the story globally. 

Just like the gold floating through Madrid, 
the truth floods the world. 

The Directorate collapses. 
A₀ is dismantled. 
And the crew disappears into digital anonymity 
