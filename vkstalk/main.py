from vkstalk import VKStalk
import sys

if __name__ == "__main__":
	#enable debug mode only if explicitly specified
	enable_debug = True if (len(sys.argv)>1 and 'debug=true' in sys.argv) else False
	#get userID from system args or input from kbd if first is empty
	user_ID = sys.argv[1] if (len(sys.argv)>1 and sys.argv[1]!='debug=true') else raw_input('User ID:') #e.g."83029348" or "alexei.dvorac"
	vk_object = VKStalk(user_ID, debug_mode = enable_debug)
	vk_object.Work()