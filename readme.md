Encrypted messaging system inside container
The crypto container works the following way
* You write and save messages
* The messages gets encrypted into container
* The container gets syncronized with remote container on remote drive (currently only flash drives are supported, but in the future other modules can be written (SSH or Exif ...)
* The messages inside container gets checked and decrypted

The cc systems works in console mode
All messages gets viewed and edited in editor (usualy vim or nano)
CC uses two encryption algorithms: RSA-4096 and Blowfish.
RSA - for signing public and private messages and for Blowfish key encryption
Blowfish - for private messages encryption

### Instalation

* git clone https://github.com/Alex014/CryptoContainer.git
* pip install pycrypto
* pip install rsa
* python cc.py - View help page
* python cc.py U+user1 - generate user user1
* python cc.py Uuser1 - select user user1
* python cc.py C+container1 - generate container1
* python cc.py Ccontainer1 - select container1
* python cc.py Fremote=/run/media/user/DDD/+upload=/run/media/user/DDD/+editor=nano - remote: remote dir to scan, upload: dir to upload containers, editor - nano 
  
### Comands
 * C: container
    - cc.py C - display all local containers
    - cc.py Ccontainer_name - select container container_name
    - cc.py C+container_name - generate new container
    - cc.py C-container_name - delete container
    - cc.py C@[container_name] - save container_name or current container if no container name given
    - cc.py C?container_name - display information about container_name
    - cc.py C^ - syncronize all containers
    - cc.py C#[container_name] - upload container_name or current container if no container name given
 * U: user and users
    - cc.py U - display all local users
    - cc.py Uuser_name - select user user_name
    - cc.py U+user_name - generate new user user_name
    - cc.py U-user_name - delete user user_name
 * P: public messages
    - cc.py P - display all local public messages
    - cc.py P+ - edit new public message (generate if it does not exist)
    - cc.py P= - edit new public message (generate if it does not exist)
    - cc.py P- - delete your last public message
    - cc.py P* - view all decrypted public messages in editor (** - inverted view)
 * M: messages from user to user
    - cc.py M - display all local private messages
    - cc.py M+[username+subject+reply_to_message] - generate new private message to username with subject
(username and subject are optional if none given you will be prompt to select them)
reply_to_message - signature of message you want to reply to (it must be message to you, type 'cc.py M*' to view all your decrypted messages), also optional
    - cc.py M+[username+subject+%2020-06-23+15:02:18] - generate new private message to username with subject and reply to message sent to you from username at 2020-06-23+15:02:18
    - cc.py M= - edit private message (selection mode)
    - cc.py M- - delete private message (selection mode)
    - cc.py M* - view all decrypted private messages in editor (** - inverted view)

 * S: status - display information about current container and current user
 * F: configuration - view or set configuration options
    - cc.py F - display all configuration options
    - cc.py Fcontainer=container1+editor=vim
    - passable configuration options: container, user, editor, remote, upload
        - container: current container
        - user: current user
        - editor: editor for editing messages
        - remote: remote path to search for remote containers
        - upload: remote path to upload the current container

### Directory structure
```
 -[containers]
   |-[container_name]
        |-[container_name]
            |-[decrypted]
                 |-container_name.json (decrypted container with your messages)
                 |-pub (public messages)
                 |-ipub (public messages inverted order)
                 |-inbox_user1 (private messages to user1)
                 |-vbox_user1 (private messages to user1 inverted order)
            |-[encrypted]
                 |-container_name.json (encrypted and sycronized container)
            |-[unsaved]
                 |-[msg] (unsaved private messages)
                 |-[pub] (unsaved public messages)
 -[etc]
   |-config.json (configuration file)
   |-users.json  (private and public keys)
```

### Uses

* python-RSA https://github.com/sybrenstuvel/python-rsa
* PyCrypto https://github.com/pycrypto/pycrypto