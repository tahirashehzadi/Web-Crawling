import os, hashlib

class FinalizeArticle:
    def DownloadAndStoreImage(self, image_url, SOURCE):
        # Image Name
        img_name = self.createMD5hash(image_url)
        img_extension = image_url.split('.')[-1].split('?')[0]
        img_name = img_name + "." + img_extension
        image_store_path = "images/" + SOURCE
        state = self.fetchImage(image_url, image_store_path, img_name)
        if state == False:
            print("Image Not avaialbe: skipping ", image_url)
            return "Error"

        return "Image Downloaded"


    def fetchImage(self, image_url, dst, img_name):
        _error = True
        counter = 0
        try:
            if not os.path.isdir(dst):
                print("WARN:Creating directory : %s" % (dst))
                os.makedirs(dst)
        except Exception as e:
            print(e)

        while _error and counter < 3:
            try:
                command = "wget %s -O %s" % (image_url, dst + '/' + img_name)
                os.system(command)
                _error = False
            except Exception as err:
                counter = counter + 1
                _error = True
                print("ImageFetchError: %s\t%s" % (image_url, err))

        if _error:
            return False
        else:
            return True

    def createMD5hash(self, url):
        url = url.encode("utf-8")
        hash_object = hashlib.md5(url)
        unique_key = hash_object.hexdigest()
        return unique_key