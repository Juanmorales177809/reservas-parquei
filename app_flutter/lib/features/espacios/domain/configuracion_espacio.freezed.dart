// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'configuracion_espacio.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ConfiguracionEspacio {

 int get espacioId; String get espacioNombre; List<int> get diasAtencion; String get horaApertura; String get horaCierre; Map<String, List<int>> get horarioAtencion; int get horasAntelacion; bool get aprobacionAutomatica;
/// Create a copy of ConfiguracionEspacio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConfiguracionEspacioCopyWith<ConfiguracionEspacio> get copyWith => _$ConfiguracionEspacioCopyWithImpl<ConfiguracionEspacio>(this as ConfiguracionEspacio, _$identity);

  /// Serializes this ConfiguracionEspacio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ConfiguracionEspacio&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.espacioNombre, espacioNombre) || other.espacioNombre == espacioNombre)&&const DeepCollectionEquality().equals(other.diasAtencion, diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other.horarioAtencion, horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.aprobacionAutomatica, aprobacionAutomatica) || other.aprobacionAutomatica == aprobacionAutomatica));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,espacioId,espacioNombre,const DeepCollectionEquality().hash(diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(horarioAtencion),horasAntelacion,aprobacionAutomatica);

@override
String toString() {
  return 'ConfiguracionEspacio(espacioId: $espacioId, espacioNombre: $espacioNombre, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, aprobacionAutomatica: $aprobacionAutomatica)';
}


}

/// @nodoc
abstract mixin class $ConfiguracionEspacioCopyWith<$Res>  {
  factory $ConfiguracionEspacioCopyWith(ConfiguracionEspacio value, $Res Function(ConfiguracionEspacio) _then) = _$ConfiguracionEspacioCopyWithImpl;
@useResult
$Res call({
 int espacioId, String espacioNombre, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, bool aprobacionAutomatica
});




}
/// @nodoc
class _$ConfiguracionEspacioCopyWithImpl<$Res>
    implements $ConfiguracionEspacioCopyWith<$Res> {
  _$ConfiguracionEspacioCopyWithImpl(this._self, this._then);

  final ConfiguracionEspacio _self;
  final $Res Function(ConfiguracionEspacio) _then;

/// Create a copy of ConfiguracionEspacio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? espacioId = null,Object? espacioNombre = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? aprobacionAutomatica = null,}) {
  return _then(ConfiguracionEspacio(
espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,espacioNombre: null == espacioNombre ? _self.espacioNombre : espacioNombre // ignore: cast_nullable_to_non_nullable
as String,diasAtencion: null == diasAtencion ? _self.diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self.horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,aprobacionAutomatica: null == aprobacionAutomatica ? _self.aprobacionAutomatica : aprobacionAutomatica // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [ConfiguracionEspacio].
extension ConfiguracionEspacioPatterns on ConfiguracionEspacio {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ConfiguracionEspacio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ConfiguracionEspacio() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ConfiguracionEspacio value)  $default,){
final _that = this;
switch (_that) {
case _ConfiguracionEspacio():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ConfiguracionEspacio value)?  $default,){
final _that = this;
switch (_that) {
case _ConfiguracionEspacio() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int espacioId,  String espacioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ConfiguracionEspacio() when $default != null:
return $default(_that.espacioId,_that.espacioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int espacioId,  String espacioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica)  $default,) {final _that = this;
switch (_that) {
case _ConfiguracionEspacio():
return $default(_that.espacioId,_that.espacioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int espacioId,  String espacioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica)?  $default,) {final _that = this;
switch (_that) {
case _ConfiguracionEspacio() when $default != null:
return $default(_that.espacioId,_that.espacioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ConfiguracionEspacio implements ConfiguracionEspacio {
  const _ConfiguracionEspacio({required this.espacioId, required this.espacioNombre, required  List<int> diasAtencion, required this.horaApertura, required this.horaCierre, required  Map<String, List<int>> horarioAtencion, required this.horasAntelacion, required this.aprobacionAutomatica}): _diasAtencion = diasAtencion,_horarioAtencion = horarioAtencion;
  factory _ConfiguracionEspacio.fromJson(Map<String, dynamic> json) => _$ConfiguracionEspacioFromJson(json);

@override final  int espacioId;
@override final  String espacioNombre;
 final  List<int> _diasAtencion;
@override List<int> get diasAtencion {
  if (_diasAtencion is EqualUnmodifiableListView) return _diasAtencion;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_diasAtencion);
}

@override final  String horaApertura;
@override final  String horaCierre;
 final  Map<String, List<int>> _horarioAtencion;
@override Map<String, List<int>> get horarioAtencion {
  if (_horarioAtencion is EqualUnmodifiableMapView) return _horarioAtencion;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_horarioAtencion);
}

@override final  int horasAntelacion;
@override final  bool aprobacionAutomatica;

/// Create a copy of ConfiguracionEspacio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ConfiguracionEspacioCopyWith<_ConfiguracionEspacio> get copyWith => __$ConfiguracionEspacioCopyWithImpl<_ConfiguracionEspacio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ConfiguracionEspacioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ConfiguracionEspacio&&(identical(other.espacioId, espacioId) || other.espacioId == espacioId)&&(identical(other.espacioNombre, espacioNombre) || other.espacioNombre == espacioNombre)&&const DeepCollectionEquality().equals(other._diasAtencion, _diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other._horarioAtencion, _horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.aprobacionAutomatica, aprobacionAutomatica) || other.aprobacionAutomatica == aprobacionAutomatica));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,espacioId,espacioNombre,const DeepCollectionEquality().hash(_diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(_horarioAtencion),horasAntelacion,aprobacionAutomatica);

@override
String toString() {
  return 'ConfiguracionEspacio(espacioId: $espacioId, espacioNombre: $espacioNombre, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, aprobacionAutomatica: $aprobacionAutomatica)';
}


}

/// @nodoc
abstract mixin class _$ConfiguracionEspacioCopyWith<$Res> implements $ConfiguracionEspacioCopyWith<$Res> {
  factory _$ConfiguracionEspacioCopyWith(_ConfiguracionEspacio value, $Res Function(_ConfiguracionEspacio) _then) = __$ConfiguracionEspacioCopyWithImpl;
@override @useResult
$Res call({
 int espacioId, String espacioNombre, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, bool aprobacionAutomatica
});




}
/// @nodoc
class __$ConfiguracionEspacioCopyWithImpl<$Res>
    implements _$ConfiguracionEspacioCopyWith<$Res> {
  __$ConfiguracionEspacioCopyWithImpl(this._self, this._then);

  final _ConfiguracionEspacio _self;
  final $Res Function(_ConfiguracionEspacio) _then;

/// Create a copy of ConfiguracionEspacio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? espacioId = null,Object? espacioNombre = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? aprobacionAutomatica = null,}) {
  return _then(_ConfiguracionEspacio(
espacioId: null == espacioId ? _self.espacioId : espacioId // ignore: cast_nullable_to_non_nullable
as int,espacioNombre: null == espacioNombre ? _self.espacioNombre : espacioNombre // ignore: cast_nullable_to_non_nullable
as String,diasAtencion: null == diasAtencion ? _self._diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self._horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,aprobacionAutomatica: null == aprobacionAutomatica ? _self.aprobacionAutomatica : aprobacionAutomatica // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
