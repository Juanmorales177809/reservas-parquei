// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'configuracion_laboratorio.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ConfiguracionLaboratorio {

 int get laboratorioId; String get laboratorioNombre; List<int> get diasAtencion; String get horaApertura; String get horaCierre; Map<String, List<int>> get horarioAtencion; int get horasAntelacion; bool get aprobacionAutomatica; bool get notificarPorCorreo;
/// Create a copy of ConfiguracionLaboratorio
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ConfiguracionLaboratorioCopyWith<ConfiguracionLaboratorio> get copyWith => _$ConfiguracionLaboratorioCopyWithImpl<ConfiguracionLaboratorio>(this as ConfiguracionLaboratorio, _$identity);

  /// Serializes this ConfiguracionLaboratorio to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ConfiguracionLaboratorio&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.laboratorioNombre, laboratorioNombre) || other.laboratorioNombre == laboratorioNombre)&&const DeepCollectionEquality().equals(other.diasAtencion, diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other.horarioAtencion, horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.aprobacionAutomatica, aprobacionAutomatica) || other.aprobacionAutomatica == aprobacionAutomatica)&&(identical(other.notificarPorCorreo, notificarPorCorreo) || other.notificarPorCorreo == notificarPorCorreo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,laboratorioId,laboratorioNombre,const DeepCollectionEquality().hash(diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(horarioAtencion),horasAntelacion,aprobacionAutomatica,notificarPorCorreo);

@override
String toString() {
  return 'ConfiguracionLaboratorio(laboratorioId: $laboratorioId, laboratorioNombre: $laboratorioNombre, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, aprobacionAutomatica: $aprobacionAutomatica, notificarPorCorreo: $notificarPorCorreo)';
}


}

/// @nodoc
abstract mixin class $ConfiguracionLaboratorioCopyWith<$Res>  {
  factory $ConfiguracionLaboratorioCopyWith(ConfiguracionLaboratorio value, $Res Function(ConfiguracionLaboratorio) _then) = _$ConfiguracionLaboratorioCopyWithImpl;
@useResult
$Res call({
 int laboratorioId, String laboratorioNombre, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, bool aprobacionAutomatica, bool notificarPorCorreo
});




}
/// @nodoc
class _$ConfiguracionLaboratorioCopyWithImpl<$Res>
    implements $ConfiguracionLaboratorioCopyWith<$Res> {
  _$ConfiguracionLaboratorioCopyWithImpl(this._self, this._then);

  final ConfiguracionLaboratorio _self;
  final $Res Function(ConfiguracionLaboratorio) _then;

/// Create a copy of ConfiguracionLaboratorio
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? laboratorioId = null,Object? laboratorioNombre = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? aprobacionAutomatica = null,Object? notificarPorCorreo = null,}) {
  return _then(ConfiguracionLaboratorio(
laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,laboratorioNombre: null == laboratorioNombre ? _self.laboratorioNombre : laboratorioNombre // ignore: cast_nullable_to_non_nullable
as String,diasAtencion: null == diasAtencion ? _self.diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self.horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,aprobacionAutomatica: null == aprobacionAutomatica ? _self.aprobacionAutomatica : aprobacionAutomatica // ignore: cast_nullable_to_non_nullable
as bool,notificarPorCorreo: null == notificarPorCorreo ? _self.notificarPorCorreo : notificarPorCorreo // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [ConfiguracionLaboratorio].
extension ConfiguracionLaboratorioPatterns on ConfiguracionLaboratorio {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ConfiguracionLaboratorio value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ConfiguracionLaboratorio value)  $default,){
final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ConfiguracionLaboratorio value)?  $default,){
final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int laboratorioId,  String laboratorioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica,  bool notificarPorCorreo)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio() when $default != null:
return $default(_that.laboratorioId,_that.laboratorioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica,_that.notificarPorCorreo);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int laboratorioId,  String laboratorioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica,  bool notificarPorCorreo)  $default,) {final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio():
return $default(_that.laboratorioId,_that.laboratorioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica,_that.notificarPorCorreo);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int laboratorioId,  String laboratorioNombre,  List<int> diasAtencion,  String horaApertura,  String horaCierre,  Map<String, List<int>> horarioAtencion,  int horasAntelacion,  bool aprobacionAutomatica,  bool notificarPorCorreo)?  $default,) {final _that = this;
switch (_that) {
case _ConfiguracionLaboratorio() when $default != null:
return $default(_that.laboratorioId,_that.laboratorioNombre,_that.diasAtencion,_that.horaApertura,_that.horaCierre,_that.horarioAtencion,_that.horasAntelacion,_that.aprobacionAutomatica,_that.notificarPorCorreo);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ConfiguracionLaboratorio implements ConfiguracionLaboratorio {
  const _ConfiguracionLaboratorio({required this.laboratorioId, required this.laboratorioNombre, required  List<int> diasAtencion, required this.horaApertura, required this.horaCierre, required  Map<String, List<int>> horarioAtencion, required this.horasAntelacion, required this.aprobacionAutomatica, required this.notificarPorCorreo}): _diasAtencion = diasAtencion,_horarioAtencion = horarioAtencion;
  factory _ConfiguracionLaboratorio.fromJson(Map<String, dynamic> json) => _$ConfiguracionLaboratorioFromJson(json);

@override final  int laboratorioId;
@override final  String laboratorioNombre;
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
@override final  bool notificarPorCorreo;

/// Create a copy of ConfiguracionLaboratorio
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ConfiguracionLaboratorioCopyWith<_ConfiguracionLaboratorio> get copyWith => __$ConfiguracionLaboratorioCopyWithImpl<_ConfiguracionLaboratorio>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ConfiguracionLaboratorioToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ConfiguracionLaboratorio&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.laboratorioNombre, laboratorioNombre) || other.laboratorioNombre == laboratorioNombre)&&const DeepCollectionEquality().equals(other._diasAtencion, _diasAtencion)&&(identical(other.horaApertura, horaApertura) || other.horaApertura == horaApertura)&&(identical(other.horaCierre, horaCierre) || other.horaCierre == horaCierre)&&const DeepCollectionEquality().equals(other._horarioAtencion, _horarioAtencion)&&(identical(other.horasAntelacion, horasAntelacion) || other.horasAntelacion == horasAntelacion)&&(identical(other.aprobacionAutomatica, aprobacionAutomatica) || other.aprobacionAutomatica == aprobacionAutomatica)&&(identical(other.notificarPorCorreo, notificarPorCorreo) || other.notificarPorCorreo == notificarPorCorreo));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,laboratorioId,laboratorioNombre,const DeepCollectionEquality().hash(_diasAtencion),horaApertura,horaCierre,const DeepCollectionEquality().hash(_horarioAtencion),horasAntelacion,aprobacionAutomatica,notificarPorCorreo);

@override
String toString() {
  return 'ConfiguracionLaboratorio(laboratorioId: $laboratorioId, laboratorioNombre: $laboratorioNombre, diasAtencion: $diasAtencion, horaApertura: $horaApertura, horaCierre: $horaCierre, horarioAtencion: $horarioAtencion, horasAntelacion: $horasAntelacion, aprobacionAutomatica: $aprobacionAutomatica, notificarPorCorreo: $notificarPorCorreo)';
}


}

/// @nodoc
abstract mixin class _$ConfiguracionLaboratorioCopyWith<$Res> implements $ConfiguracionLaboratorioCopyWith<$Res> {
  factory _$ConfiguracionLaboratorioCopyWith(_ConfiguracionLaboratorio value, $Res Function(_ConfiguracionLaboratorio) _then) = __$ConfiguracionLaboratorioCopyWithImpl;
@override @useResult
$Res call({
 int laboratorioId, String laboratorioNombre, List<int> diasAtencion, String horaApertura, String horaCierre, Map<String, List<int>> horarioAtencion, int horasAntelacion, bool aprobacionAutomatica, bool notificarPorCorreo
});




}
/// @nodoc
class __$ConfiguracionLaboratorioCopyWithImpl<$Res>
    implements _$ConfiguracionLaboratorioCopyWith<$Res> {
  __$ConfiguracionLaboratorioCopyWithImpl(this._self, this._then);

  final _ConfiguracionLaboratorio _self;
  final $Res Function(_ConfiguracionLaboratorio) _then;

/// Create a copy of ConfiguracionLaboratorio
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? laboratorioId = null,Object? laboratorioNombre = null,Object? diasAtencion = null,Object? horaApertura = null,Object? horaCierre = null,Object? horarioAtencion = null,Object? horasAntelacion = null,Object? aprobacionAutomatica = null,Object? notificarPorCorreo = null,}) {
  return _then(_ConfiguracionLaboratorio(
laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,laboratorioNombre: null == laboratorioNombre ? _self.laboratorioNombre : laboratorioNombre // ignore: cast_nullable_to_non_nullable
as String,diasAtencion: null == diasAtencion ? _self._diasAtencion : diasAtencion // ignore: cast_nullable_to_non_nullable
as List<int>,horaApertura: null == horaApertura ? _self.horaApertura : horaApertura // ignore: cast_nullable_to_non_nullable
as String,horaCierre: null == horaCierre ? _self.horaCierre : horaCierre // ignore: cast_nullable_to_non_nullable
as String,horarioAtencion: null == horarioAtencion ? _self._horarioAtencion : horarioAtencion // ignore: cast_nullable_to_non_nullable
as Map<String, List<int>>,horasAntelacion: null == horasAntelacion ? _self.horasAntelacion : horasAntelacion // ignore: cast_nullable_to_non_nullable
as int,aprobacionAutomatica: null == aprobacionAutomatica ? _self.aprobacionAutomatica : aprobacionAutomatica // ignore: cast_nullable_to_non_nullable
as bool,notificarPorCorreo: null == notificarPorCorreo ? _self.notificarPorCorreo : notificarPorCorreo // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
