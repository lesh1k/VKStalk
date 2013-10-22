from vkstalk import VKStalk

if __name__ == "__main__":
	#Keyboard input of user ID
	user_ID = raw_input('User ID:') #e.g."83029348"
	vk_object = VKStalk(user_ID)
	vk_object.work()