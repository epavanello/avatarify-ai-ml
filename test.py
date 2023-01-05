import s3
s3_client = s3.getS3Client()

s3_client.upload_file("/home/ubuntu/dreambooth/models/f456fdce-640e-4ec2-8dd3-63854f4ac2d3/f456fdce-640e-4ec2-8dd3-63854f4ac2d3.ckpt", 'avatarify-ai-storage',
                      "f456fdce-640e-4ec2-8dd3-63854f4ac2d3/f456fdce-640e-4ec2-8dd3-63854f4ac2d3.ckpt")

s3_client.upload_file("/home/ubuntu/dreambooth/models/9deb7a22-9609-46e1-90da-7754f8dccddd/9deb7a22-9609-46e1-90da-7754f8dccddd.ckpt", 'avatarify-ai-storage',
                      "9deb7a22-9609-46e1-90da-7754f8dccddd/9deb7a22-9609-46e1-90da-7754f8dccddd.ckpt" )
