from data.loader import dp, bot
from data.config import ConfigBot
from data.config_Keyboard import ConfigReplyKeyboard, ConfigRoleUsers, ConfigVerifyUsers
from data.loader_keyboard import LoaderReplyKeyboards, LoaderInlineKeyboards

from data.version_db import get_bot_version
from data.user_db import load_user_data, is_user_in_data, save_user_data
from data.states_groups import StartState

from misc.libraries import types, FSMContext
from misc.loggers import logger

from keyboards.users.ReplyKeyboard.ReplyKeyboard_all import hide_keyboard

"""Создаем обработчик команды /start"""
@dp.message_handler(commands=("start"))
async def start_command(message: types.Message) -> LoaderReplyKeyboards:
	"""Объявляем переменные с выводом данных о пользователе, версии бота и клавиатуры"""
	USER_DATA_DB = load_user_data()
	VERSION_BOT = get_bot_version()

	keyboard_start = LoaderReplyKeyboards(message).KEYBOARDS_START

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(message)

		if is_user_in_data(USER_ID, USER_DATA_DB):
			"""Объявляем переменную с выводом текущей версии пользователя"""
			USER_VERSION_BOT = ConfigBot.USERVERSIONBOT(message)

			if USER_VERSION_BOT == VERSION_BOT:
				await message.answer(f"{ConfigBot.GETCURRENTHOUR()} <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a> НАЖМИТЕ КНОПКУ ЗАПУСТИТЬ БОТА", reply_markup=keyboard_start)
			
			elif USER_VERSION_BOT != VERSION_BOT:
				await message.answer(f"💬 <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>! Рады сообщить, что вышла <b>новая версия</b> нашего бота с улучшениями и новыми возможностями.\n\n" 
									"❕ Для получения всех новинок и обновлений, пожалуйста, воспользуйтесь командой <b><code>/update</code></b>.\n\n" 
									"Спасибо за ваше внимание и активное использование нашего бота! 🤍")
					
			else:
				logger.warning("⚠️ USER_VERSION_BOT не ровняется к текущей версии бота.")

		elif not is_user_in_data(USER_ID, USER_DATA_DB):
			await message.answer("Привет это бот", reply_markup=keyboard_start)
			
		else:
			logger.error("⚠️ Произошла непредвиденная ошибка с проверкой, существует пользователь в базе данных.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)

"""Создаем главный обработчик для команды /start"""
@dp.message_handler(lambda message: message.text == f"{ConfigReplyKeyboard().RUN_BOT}")
async def start_handler(message: types.Message) -> StartState:
	"""Объявляем переменную с выводом информации о пользователе"""
	USER_DATA_DB = load_user_data()

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(message)

		if is_user_in_data(USER_ID, USER_DATA_DB):
			await message.answer(f"💬 Для использования бота, <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>, пожалуйста, введите ваш <b>пароль</b>.", reply_markup=hide_keyboard())

			"""Переходим в фазу, где пользователь вводит придуманный пароль"""
			await StartState.RegistrationUserState.set()

		elif not is_user_in_data(USER_ID, USER_DATA_DB):
			"""Сохраняем USER_ID Пользователя и создаем дополнительные параметры, для следующих функций"""
			USER_DATA_DB[str(ConfigBot.USERID(message))] = {
				"USER_LAST_NAME": ConfigBot.USERLASTNAME(message),
				"USER_NAME": f"https://t.me/{ConfigBot.USERNAME(message)}",
				"VERSION_BOT": ConfigBot().VERSION
			}
			
			save_user_data(USER_DATA_DB)

			await message.answer(f"💬 <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>, для начало регистрации в нашем боте, пожалуйста, придумайте ваш надежный <b>пароль</b>.\n\n"
								 "❕ Убедитесь, что он состоит из <b>12 символов</b>, включая хотя бы <b>одну цифру</b>.", reply_markup=hide_keyboard())
			
			"""Переходим в фазу, где пользователь вводит придуманный пароль"""
			await StartState.RegistrationUserState.set()
		
		else:
			logger.error("⚠️ Произошла непредвиденная ошибка с проверкой, существует пользователь в базе данных.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)

"""Создаем обработчика фазы, где пользователь вводит придуманный пароль"""
@dp.message_handler(state=StartState.RegistrationUserState)
async def password_handler(message: types.Message, state: FSMContext) -> StartState:
	"""Объявляем переменную с выводом информации о пользователе"""
	USER_DATA_DB = load_user_data()

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(message)

		"""Проверяем есть ли пользователь в базе данных"""
		if is_user_in_data(USER_ID, USER_DATA_DB):
			"""Объявляем переменную с выводом информации о пользователе: USER_PASSWORD, USER_MESSAGE"""
			USER_PASSWORD = ConfigBot.USERPASSWORD(message)
			USER_MESSAGE = ConfigBot.USERMESSAGE(message)

			if USER_PASSWORD == None:
				"""Проверяем условия ввода пароль от пользователя"""
				if len(USER_MESSAGE) < 12 or not any(char.isalpha() for char in USER_MESSAGE) or not any(char.isdigit() for char in USER_MESSAGE):
					await message.answer("⚠️ Пароль должен состоять из <b>12 символов</b> и содержать хотя бы <b>одну цифру</b>.")

				else:
					"""Сохраняем пароль пользователя в базе данных"""
					USER_DATA_DB[str(USER_ID)]["USER_PASSWORD"] = USER_MESSAGE
					
					save_user_data(USER_DATA_DB)

					"""Объявляем переменную с выводом информации о пользователе: USER_NATION"""
					USER_NATION = ConfigBot.USERNATION(message)

					"""Проверяем есть ли уже страна у пользователя или нет"""
					if USER_NATION == None:
						await message.answer(f"💬 <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>, отлично идем! Теперь уточним вашу <b>нацию</b> или <b>страну</b>.\n\n"
											"❕ Пожалуйста, укажите свою <b>национальность</b> или <b>страну проживания</b>.")

						"""Переходим в фазу, где вводит свою нацию/страну"""
						await StartState.NationUserState.set()
						
					elif USER_NATION != None:
						"""Переходим в обработчик для входа в аккаунт"""
						await start_handler(message)
					
					else:
						logger.warning("⚠️ USER_NATION не ровняется None или не None.")

			elif USER_PASSWORD == USER_MESSAGE:
				"""Выводим клавиатуры для обработчика главного меню"""
				keyboard_menu = LoaderReplyKeyboards(message).KEYBOARDS_MENU

				await message.answer(f"💬 Прекрасно, <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>! Ваш пароль успешно <b>подтвержден</b>. Добро пожаловать обратно!\n\n"
						 			 f"Если у вас есть какие-либо вопросы или нужна помощь, не стесняйтесь спрашивать нашу <a href='https://t.me/{ConfigBot().AUTHOR}'><b>администрацию</b></a>.", reply_markup=keyboard_menu)
				
				await state.finish()

			elif USER_PASSWORD != USER_MESSAGE:
				"""Выводим Inline клавиатуры для обработчика восстановления пароля"""
				inline_keyboard_recovery = LoaderInlineKeyboards(message).INLINE_KEYBOARDS_RECOVERY

				await message.answer("⚠️ Кажется, что пароль введен <b>неверно</b>. Пожалуйста, проверьте свои данные и попробуйте еще раз.\n\n"
						 			 f"❕ Если у вас возникли проблемы с доступом, вы можете воспользоваться функцией <b>восстановления пароля</b> или связаться с нашей <a href='https://t.me/{ConfigBot().AUTHOR}'><b>администрацией</b></a>.", reply_markup=inline_keyboard_recovery)
			
			else:
				logger.warning("⚠️ Произошла ошибка с USER_PASSWORD.")
		else:
			logger.warning(f"⚠️ Незарегистрированный пользователь [@{ConfigBot.USERNAME(message)}] попытался вести пароль для входа в систему.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)

"""Создаем обработчика фазы, где пользователь вводит нацию/страну"""
@dp.message_handler(state=StartState.NationUserState)
async def nation_handler(message: types.Message, state: FSMContext) -> FSMContext:
	"""Объявляем переменную с выводом информации о пользователе"""
	USER_DATA_DB = load_user_data()

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(message)

		"""Проверяем есть ли пользователь в базе данных"""
		if is_user_in_data(USER_ID, USER_DATA_DB):
			"""Объявляем переменную с выводом информации о пользователе: USER_MESSAGE"""
			USER_MESSAGE = ConfigBot.USERMESSAGE(message)

			"""Объявляем переменные с отправкой данных о введенной нации пользователем"""
			ENGLISH_NAME = ConfigBot.TRANSLATETOENGLISH(USER_MESSAGE)
			COUNTRY_INFO = ConfigBot.GETCOUNTRYINFO(ENGLISH_NAME)

			if COUNTRY_INFO:
				"""Выводим клавиатуры для обработчика главного меню"""
				keyboard_menu = LoaderReplyKeyboards(message).KEYBOARDS_MENU

				"""Сохраняем название страны который пользователь ввел"""
				USER_DATA_DB[str(ConfigBot.USERID(message))]["NATION_USER"] = ConfigBot.USERMESSAGE(message)
				USER_DATA_DB[str(ConfigBot.USERID(message))]["BOT_ID"] = ConfigBot.GETBOTID()
				USER_DATA_DB[str(ConfigBot.USERID(message))]["USER_ROLE"] = ConfigRoleUsers().USER_NEW
				USER_DATA_DB[str(ConfigBot.USERID(message))]["NAME_USER_ROLE"] = ConfigRoleUsers().USER_NAME_NEW

				USER_DATA_DB[str(ConfigBot.USERID(message))]["VERIFY_DATA"] = {
					"STATUS_VERIFY_USER": ConfigVerifyUsers().NOPE_VERIFY_USER,
					"VERIFY_USER": False,
					"CONSIDERATION_VERIFY_USER": False
				}

				save_user_data(USER_DATA_DB)

				await message.answer(f"💬 <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>, поздравляем! <b>Регистрация завершена</b>. Теперь вы можете наслаждаться всеми возможностями нашего бота.\n\n"
						 			 f"Если у вас возникнут вопросы или нужна помощь, не стесняйтесь обращаться нашей <a href='https://t.me/{ConfigBot().AUTHOR}'><b>администрации</b></a>.", reply_markup=keyboard_menu)
				
				await state.finish()

			elif not COUNTRY_INFO:
				await message.answer("⚠️ Похоже, что вы ввели <b>несуществующую</b> страну. Пожалуйста, введите <b>настоящую</b> страну.")
			
			else:
				logger.warning("COUNTRY_INFO не ровняется никакой стране или нации.")
		else:
			logger.warning(f"⚠️ Незарегистрированный пользователь [@{ConfigBot.USERNAME(message)}] попытался ввести нацию/страну.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)

"""Создаем обработчик для восстановления пароля от учетной запили пользователя"""
@dp.callback_query_handler(lambda callback_data: callback_data.data == "RECOVERY_PASSWORD", state=StartState.RegistrationUserState)
async def recovery_password(callback_query: types.CallbackQuery):
	"""Загружаем базу данных о пользователе"""
	USER_DATA_DB = load_user_data()

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(callback_query)

		"""Проверяем есть ли пользователь в базе данных"""
		if is_user_in_data(USER_ID, USER_DATA_DB):
			await bot.edit_message_text(f"💬 <a href='https://t.me/{ConfigBot.USERNAME(callback_query)}'>{ConfigBot.USERLASTNAME(callback_query)}</a>, для восстановления пароля, введите ваш <b>BOT_ID</b>\n\n"
										f"❕ Если у вас возникнут вопросы или нужна помощь, не стесняйтесь обращаться нашей <a href='https://t.me/{ConfigBot().AUTHOR}'><b>администрации</b></a>.", callback_query.from_user.id, callback_query.message.message_id)

			"""Переходим в фазу, где вводят свой USER_ID"""
			await StartState.RecoveryPasswordState.set()

		else:
			logger.warning(f"⚠️ Незарегистрированный пользователь [@{ConfigBot.USERNAME(callback_query)}] попытался восстановить пароль.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)

"""Создаем обработчик фазу, где пользователь вводит свой USER_ID"""
@dp.message_handler(state=StartState.RecoveryPasswordState)
async def recovery_password_handler(message: types.Message):
	"""Загружаем базу данных о пользователе"""
	USER_DATA_DB = load_user_data()

	try:
		"""Объявляем переменную с выводом информации о пользователе: USER_ID"""
		USER_ID = ConfigBot.USERID(message)

		"""Проверяем есть ли пользователь в базе данных"""
		if is_user_in_data(USER_ID, USER_DATA_DB):
			"""Объявляем переменную с выводом информации о пользователе: USER_BOT_ID, USER_MESSAGE"""
			USER_BOT_ID = ConfigBot.USERBOTID(message)
			USER_MESSAGE = ConfigBot.USERMESSAGE(message)

			if USER_BOT_ID == USER_MESSAGE:
				"""Меняет текущий пароль пользователя на None"""
				USER_DATA_DB[str(USER_ID)]["USER_PASSWORD"] = None

				save_user_data(USER_DATA_DB)

				await message.answer(f"💬 Отлично, <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>! <b>BOT_ID</b> успешно <b>подтвержден</b>.\n\n"
						 			 "Теперь вы можете безопасно ввести <b>новый пароль</b> для вашей учетной записи.\n\n"
						 			 "❕ Убедитесь, что он состоит из <b>12 символов</b>, включая хотя бы <b>одну цифру</b>.")

				"""Переходим в фазу, где вводят новый пароль"""
				await StartState.RegistrationUserState.set()

			elif USER_BOT_ID != USER_MESSAGE:
				await message.answer(f"⚠️ Извините, <a href='https://t.me/{ConfigBot.USERNAME(message)}'>{ConfigBot.USERLASTNAME(message)}</a>, но похоже, что введен неверный <b>BOT_ID</b>. Пожалуйста, убедитесь, что вы вводите правильные данные, и повторите попытку.\n\n"
						 			 f"❕ Если у вас возникли проблемы с доступом, не стесняйтесь обратиться за помощью к нашей <a href='https://t.me/{ConfigBot().AUTHOR}'><b>администрации</b></a>.")
			
			else:
				logger.warning("⚠️ USER_BOT_ID не ровняется введеному пользователем BOT_ID")
		else:
			logger.warning(f"⚠️ Незарегистрированный пользователь [@{ConfigBot.USERNAME(message)}] попытался ввести свой BOT_ID.")
	except Exception as e:
		logger.error("⚠️ Произошла непредвиденная ошибка: %s", e)