<?php
/**
 * Справочники значений и реестр полей ресурса.
 *
 * Один источник правды для meta-полей, панели редактора, колонок списка,
 * блоков и seed. Ключи и значения — ровно из brief §5.1, слова — из docs/VOICE.md.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Справочники enum: ключ поля → ключ значения → слово словаря.
 *
 * @return array<string, array<string, string>>
 */
function designstack_core_enums(): array {
	static $enums = null;

	if ( null !== $enums ) {
		return $enums;
	}

	$enums = array(
		'pricing'    => array(
			'free'     => __( 'Бесплатно', 'designstack-core' ),
			'freemium' => __( 'Есть бесплатный тариф', 'designstack-core' ),
			'paid'     => __( 'Платно', 'designstack-core' ),
			'trial'    => __( 'Пробный период', 'designstack-core' ),
		),
		'ru_open'    => array(
			'open'     => __( 'Открывается из РФ', 'designstack-core' ),
			'unstable' => __( 'Открывается с перебоями', 'designstack-core' ),
			'blocked'  => __( 'Недоступен из РФ', 'designstack-core' ),
		),
		'ru_payment' => array(
			'payable'      => __( 'Оплачивается из РФ', 'designstack-core' ),
			'intermediary' => __( 'Через посредника', 'designstack-core' ),
			'no_payment'   => __( 'Не оплатить из РФ', 'designstack-core' ),
			'ru_native'    => __( 'Российский', 'designstack-core' ),
		),
		'language'   => array(
			'ru'    => __( 'На русском', 'designstack-core' ),
			'en'    => __( 'На английском', 'designstack-core' ),
			'multi' => __( 'RU + EN', 'designstack-core' ),
		),
		'status'     => array(
			'active'  => __( 'Активен', 'designstack-core' ),
			'changed' => __( 'Условия изменились', 'designstack-core' ),
			'dead'    => __( 'Закрыт', 'designstack-core' ),
		),
		'platforms'  => array(
			'web'          => __( 'Веб', 'designstack-core' ),
			'mac'          => __( 'macOS', 'designstack-core' ),
			'win'          => __( 'Windows', 'designstack-core' ),
			'ios'          => __( 'iOS', 'designstack-core' ),
			'android'      => __( 'Android', 'designstack-core' ),
			'figma-plugin' => __( 'Плагин Figma', 'designstack-core' ),
		),
		'format'     => array(
			'course'  => __( 'Курс', 'designstack-core' ),
			'book'    => __( 'Книга', 'designstack-core' ),
			'article' => __( 'Статья', 'designstack-core' ),
			'video'   => __( 'Видео', 'designstack-core' ),
			'podcast' => __( 'Подкаст', 'designstack-core' ),
			'guide'   => __( 'Гайд', 'designstack-core' ),
		),
		'license'    => array(
			'free-commercial' => __( 'Бесплатно, в том числе в коммерции', 'designstack-core' ),
			'personal-only'   => __( 'Только личное', 'designstack-core' ),
			'cc-by'           => __( 'CC BY', 'designstack-core' ),
			'paid'            => __( 'Платная лицензия', 'designstack-core' ),
		),
		'cyrillic'   => array(
			'yes'     => __( 'есть', 'designstack-core' ),
			'partial' => __( 'частично', 'designstack-core' ),
			'no'      => __( 'нет', 'designstack-core' ),
		),
		'platform'   => array(
			'telegram'   => __( 'Telegram', 'designstack-core' ),
			'discord'    => __( 'Discord', 'designstack-core' ),
			'website'    => __( 'сайт', 'designstack-core' ),
			'newsletter' => __( 'рассылка', 'designstack-core' ),
		),
		'activity'   => array(
			'daily'  => __( 'Пишут ежедневно', 'designstack-core' ),
			'weekly' => __( 'Пишут еженедельно', 'designstack-core' ),
			'rare'   => __( 'Пишут редко', 'designstack-core' ),
		),
	);

	return $enums;
}

/**
 * Известные форматы файлов ассетов: слаг → как пишем.
 *
 * Список открытый: незнакомый формат сохраняется слагом и показывается заглавными.
 *
 * @return array<string, string>
 */
function designstack_core_file_formats(): array {
	return array(
		'figma'  => 'Figma',
		'sketch' => 'Sketch',
		'penpot' => 'Penpot',
		'svg'    => 'SVG',
		'png'    => 'PNG',
		'pdf'    => 'PDF',
		'otf'    => 'OTF',
		'ttf'    => 'TTF',
		'woff2'  => 'WOFF2',
		'ai'     => 'AI',
		'psd'    => 'PSD',
		'xd'     => 'XD',
	);
}

/**
 * Реестр полей ресурса.
 *
 * Ключи:
 * group    — common | tool | learning | asset | community (в какой fieldset панели);
 * label    — подпись из docs/VOICE.md;
 * control  — url | text | textarea | date | select | multiselect | checkbox | number | posts | terms;
 * type     — тип значения: string | boolean | integer;
 * multiple — true у полей со списком значений (хранятся отдельными строками meta);
 * enum     — ключ справочника designstack_core_enums();
 * hint     — подсказка под полем в редакторе;
 * max      — предел длины строки.
 *
 * @return array<string, array<string, mixed>>
 */
function designstack_core_fields(): array {
	static $fields = null;

	if ( null !== $fields ) {
		return $fields;
	}

	$fields = array(
		'url'            => array(
			'group'   => 'common',
			'label'   => __( 'Адрес ресурса', 'designstack-core' ),
			'control' => 'url',
			'type'    => 'string',
		),
		'verdict'        => array(
			'group'   => 'common',
			'label'   => __( 'Вердикт', 'designstack-core' ),
			'control' => 'text',
			'type'    => 'string',
			'max'     => 120,
			'hint'    => __( 'Одна фраза-вывод в карточке, до 120 знаков.', 'designstack-core' ),
		),
		'review_for'     => array(
			'group'   => 'common',
			'label'   => __( 'Кому подходит', 'designstack-core' ),
			'control' => 'textarea',
			'type'    => 'string',
			'hint'    => __( 'Первая часть оценки куратора.', 'designstack-core' ),
		),
		'review_why'     => array(
			'group'   => 'common',
			'label'   => __( 'За что', 'designstack-core' ),
			'control' => 'textarea',
			'type'    => 'string',
			'hint'    => __( 'Вторая часть оценки куратора.', 'designstack-core' ),
		),
		'review_not'     => array(
			'group'   => 'common',
			'label'   => __( 'Когда не подойдёт', 'designstack-core' ),
			'control' => 'textarea',
			'type'    => 'string',
			'hint'    => __( 'Третья часть оценки. Без неё ресурс не публикуется: публикация вернёт запись на утверждение (D32).', 'designstack-core' ),
		),
		'pricing'        => array(
			'group'   => 'common',
			'label'   => __( 'Цена', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'pricing',
		),
		'price_note'     => array(
			'group'   => 'common',
			'label'   => __( 'Заметка о цене', 'designstack-core' ),
			'control' => 'text',
			'type'    => 'string',
			'hint'    => __( 'Например: от $12 в месяц; бесплатно для студентов.', 'designstack-core' ),
		),
		'ru_open'        => array(
			'group'   => 'common',
			'label'   => __( 'Доступ из РФ', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'ru_open',
			'hint'    => __( 'Ставится только по проверке с российского IP.', 'designstack-core' ),
		),
		'ru_payment'     => array(
			'group'   => 'common',
			'label'   => __( 'Оплата из РФ', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'ru_payment',
			'hint'    => __( 'У бесплатного ресурса не заполняется (D28).', 'designstack-core' ),
		),
		'ru_alternative' => array(
			'group'    => 'common',
			'label'    => __( 'Аналог из России', 'designstack-core' ),
			'control'  => 'posts',
			'type'     => 'integer',
			'multiple' => true,
			'hint'     => __( 'Опубликованные ресурсы каталога. Связь простая: подробности пары — в v1.1 вместе со страницей «Замена» (D61).', 'designstack-core' ),
		),
		'language'       => array(
			'group'   => 'common',
			'label'   => __( 'Язык', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'language',
		),
		'checked_at'     => array(
			'group'   => 'common',
			'label'   => __( 'Дата проверки', 'designstack-core' ),
			'control' => 'date',
			'type'    => 'string',
		),
		'status'         => array(
			'group'   => 'common',
			'label'   => __( 'Состояние записи', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'status',
		),
		'affiliate_url'  => array(
			'group'   => 'common',
			'label'   => __( 'Партнёрская ссылка', 'designstack-core' ),
			'control' => 'url',
			'type'    => 'string',
			'hint'    => __( 'Заложено на будущее, в MVP не используется.', 'designstack-core' ),
		),
		'platforms'      => array(
			'group'    => 'tool',
			'label'    => __( 'Платформы', 'designstack-core' ),
			'control'  => 'multiselect',
			'type'     => 'string',
			'multiple' => true,
			'enum'     => 'platforms',
		),
		'has_free_tier'  => array(
			'group'   => 'tool',
			'label'   => __( 'Бесплатный тариф', 'designstack-core' ),
			'control' => 'checkbox',
			'type'    => 'boolean',
		),
		'ai_features'    => array(
			'group'   => 'tool',
			'label'   => __( 'ИИ-функции', 'designstack-core' ),
			'control' => 'checkbox',
			'type'    => 'boolean',
		),
		'format'         => array(
			'group'   => 'learning',
			'label'   => __( 'Формат', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'format',
		),
		'duration'       => array(
			'group'   => 'learning',
			'label'   => __( 'Длительность', 'designstack-core' ),
			'control' => 'text',
			'type'    => 'string',
			'hint'    => __( 'Например: 6 часов; 300 страниц.', 'designstack-core' ),
		),
		'certificate'    => array(
			'group'   => 'learning',
			'label'   => __( 'Сертификат', 'designstack-core' ),
			'control' => 'checkbox',
			'type'    => 'boolean',
		),
		'skill_junior'   => array(
			'group'    => 'learning',
			'label'    => __( 'Поднимает навык до junior', 'designstack-core' ),
			'control'  => 'terms',
			'taxonomy' => 'skill',
			'type'     => 'integer',
			'multiple' => true,
		),
		'skill_middle'   => array(
			'group'    => 'learning',
			'label'    => __( 'Поднимает навык до middle', 'designstack-core' ),
			'control'  => 'terms',
			'taxonomy' => 'skill',
			'type'     => 'integer',
			'multiple' => true,
		),
		'skill_senior'   => array(
			'group'    => 'learning',
			'label'    => __( 'Поднимает навык до senior', 'designstack-core' ),
			'control'  => 'terms',
			'taxonomy' => 'skill',
			'type'     => 'integer',
			'multiple' => true,
		),
		'license'        => array(
			'group'   => 'asset',
			'label'   => __( 'Лицензия', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'license',
		),
		'file_format'    => array(
			'group'    => 'asset',
			'label'    => __( 'Формат файла', 'designstack-core' ),
			'control'  => 'text',
			'type'     => 'string',
			'multiple' => true,
			'hint'     => __( 'Через запятую: figma, svg, otf.', 'designstack-core' ),
		),
		'cyrillic'       => array(
			'group'   => 'asset',
			'label'   => __( 'Кириллица', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'cyrillic',
		),
		'assets_count'   => array(
			'group'   => 'asset',
			'label'   => __( 'Количество', 'designstack-core' ),
			'control' => 'number',
			'type'    => 'integer',
		),
		'platform'       => array(
			'group'   => 'community',
			'label'   => __( 'Платформа', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'platform',
		),
		'audience_size'  => array(
			'group'   => 'community',
			'label'   => __( 'Размер аудитории', 'designstack-core' ),
			'control' => 'text',
			'type'    => 'string',
			'hint'    => __( 'Оценка с датой: ≈ 12 000, 09.2026.', 'designstack-core' ),
		),
		'activity'       => array(
			'group'   => 'community',
			'label'   => __( 'Активность', 'designstack-core' ),
			'control' => 'select',
			'type'    => 'string',
			'enum'    => 'activity',
		),
		'is_jobs'        => array(
			'group'   => 'community',
			'label'   => __( 'Вакансии', 'designstack-core' ),
			'control' => 'checkbox',
			'type'    => 'boolean',
		),
	);

	return $fields;
}

/**
 * Названия групп полей: ключ типа → подпись fieldset в панели.
 *
 * @return array<string, string>
 */
function designstack_core_field_groups(): array {
	return array(
		'common'    => __( 'Общие', 'designstack-core' ),
		'tool'      => __( 'Инструмент', 'designstack-core' ),
		'learning'  => __( 'Учебный материал', 'designstack-core' ),
		'asset'     => __( 'Ассет', 'designstack-core' ),
		'community' => __( 'Сообщество', 'designstack-core' ),
	);
}

/**
 * Слово справочника по ключу значения.
 *
 * @param string $enum  Ключ справочника.
 * @param string $value Ключ значения.
 * @return string Слово или пустая строка.
 */
function designstack_core_enum_label( string $enum, string $value ): string {
	$enums = designstack_core_enums();

	return $enums[ $enum ][ $value ] ?? '';
}
